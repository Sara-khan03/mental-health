# app.py
# MindCare prototype - Chatbot + Mood Tracker + Crisis Detection + Connect to Professionals
# Run: python -m streamlit run app.py

import os
import sqlite3
from datetime import datetime
import streamlit as st
from textblob import TextBlob
import pandas as pd
import plotly.express as px
import smtplib
from email.message import EmailMessage

# Optional OpenAI usage (only if configured)
try:
    import openai
except Exception:
    openai = None

# ---------------------------
# Config & DB
# ---------------------------
st.set_page_config(page_title="MindCare — Safer Prototype", layout="wide", page_icon="🧠")

DB_PATH = "mindcare.db"
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    detail TEXT,
                    sentiment REAL,
                    is_crisis INTEGER,
                    ts TEXT
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS moods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mood_label TEXT,
                    score INTEGER,
                    note TEXT,
                    ts TEXT
                )""")
    conn.commit()
    return conn

conn = init_db()
cur = conn.cursor()

# ---------------------------
# Utilities
# ---------------------------
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die", "hurtd myself", "die", "i can't go on",
    "i'll kill myself", "killme", "i want to end"
]

def analyze_sentiment(text: str):
    try:
        return round(TextBlob(text).sentiment.polarity, 3)
    except Exception:
        return 0.0

def detect_crisis(text: str, sentiment: float):
    txt = text.lower()
    if any(k in txt for k in CRISIS_KEYWORDS):
        return True
    if sentiment <= -0.6:
        return True
    return False

def log_event(event_type, detail, sentiment, is_crisis):
    ts = datetime.utcnow().isoformat()
    cur.execute("INSERT INTO events (type, detail, sentiment, is_crisis, ts) VALUES (?, ?, ?, ?, ?)",
                (event_type, detail[:2000], sentiment, int(bool(is_crisis)), ts))
    conn.commit()

def save_mood(label, score, note=""):
    ts = datetime.utcnow().isoformat()
    cur.execute("INSERT INTO moods (mood_label, score, note, ts) VALUES (?, ?, ?, ?)",
                (label, score, note[:1000], ts))
    conn.commit()

def get_moods_df():
    df = pd.read_sql_query("SELECT * FROM moods ORDER BY id ASC", conn)
    return df

# ---------------------------
# Optional: SMTP send (only if configured)
# Store SMTP config in Streamlit secrets or environment variables
# ---------------------------
def send_email_via_smtp(to_email, subject, body):
    # Use Streamlit secrets if available
    smtp_host = st.secrets.get("smtp_host") if "smtp_host" in st.secrets else os.getenv("SMTP_HOST")
    smtp_port = int(st.secrets.get("smtp_port")) if "smtp_port" in st.secrets else int(os.getenv("SMTP_PORT") or 587)
    smtp_user = st.secrets.get("smtp_user") if "smtp_user" in st.secrets else os.getenv("SMTP_USER")
    smtp_pass = st.secrets.get("smtp_pass") if "smtp_pass" in st.secrets else os.getenv("SMTP_PASS")
    from_addr = smtp_user
    if not smtp_host or not smtp_user or not smtp_pass:
        return False, "SMTP not configured. Set SMTP_HOST, SMTP_USER, SMTP_PASS in environment or Streamlit secrets."
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to_email
        msg.set_content(body)
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True, "Email sent"
    except Exception as e:
        return False, str(e)

# ---------------------------
# App UI
# ---------------------------
# basic CSS load (if exists)
if os.path.exists("style.css"):
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Prototype Controls")
openai_key = st.sidebar.text_input("OpenAI API key (optional)", type="password")
st.sidebar.markdown("---")
st.sidebar.info("This prototype is not a medical tool. In emergency, call local services.")
st.sidebar.markdown("**Emergency Helplines (India)**\n- Vandrevala: 9152987821\n- iCALL: 9152987821\n\n**Global**: 988 (where applicable)")

# Quick emergency contact form (optional)
st.sidebar.markdown("---")
st.sidebar.subheader("Emergency contact (optional)")
trusted_name = st.sidebar.text_input("Trusted contact name", "")
trusted_phone = st.sidebar.text_input("Trusted contact phone (with country code)", "")
trusted_email = st.sidebar.text_input("Trusted contact email", "")

# Main layout
st.title("MindCare — Safer Prototype")
st.subheader("Chatbot • Mood Tracker • Crisis detection • Connect to professionals")

tabs = st.tabs(["Chatbot", "Mood Tracker", "Resources & Connect"])

# ---------------------------
# Tab: Chatbot
# ---------------------------
with tabs[0]:
    st.header("Chat with MindCare")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # show chat
    for msg in st.session_state.chat_history:
        role = msg["role"]
        content = msg["text"]
        if role == "user":
            st.markdown(f"**You:** {content}")
        else:
            st.markdown(f"**Bot:** {content}")

    user_msg = st.text_area("Type your message (be honest) — we detect risk words", height=120)
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Send"):
            if not user_msg.strip():
                st.warning("Please type something")
            else:
                sentiment = analyze_sentiment(user_msg)
                is_crisis = detect_crisis(user_msg, sentiment)
                log_event("chat", user_msg, sentiment, is_crisis)
                st.session_state.chat_history.append({"role":"user","text":user_msg})
                # decide reply
                reply = ""
                # If OpenAI key present, use model (optional)
                if openai_key and openai:
                    try:
                        openai.api_key = openai_key
                        resp = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role":"system","content":"You are a supportive mental health assistant."},
                                      {"role":"user","content":user_msg}],
                            max_tokens=300
                        )
                        reply = resp.choices[0].message.content.strip()
                    except Exception as e:
                        reply = "Sorry, AI service unavailable. Try the self-care tools or resources."
                else:
                    # simple empathetic fallback
                    if sentiment > 0.2:
                        reply = "I'm glad you're doing okay. Tell me more if you'd like."
                    elif sentiment < -0.2:
                        reply = "I hear you — that sounds really difficult. Would you like breathing guidance or to contact help?"
                    else:
                        reply = "Thanks for sharing. Small steps can help — would you like a short exercise?"

                # append and show
                st.session_state.chat_history.append({"role":"bot","text":reply})
                st.experimental_rerun()  # re-render to show updated chat

    with col2:
        st.markdown("### Quick actions")
        if st.button("Short breathing exercise"):
            st.success("Try: Inhale 4s — Hold 4s — Exhale 6s — Repeat 6 times.")
        if st.button("Report urgent content"):
            st.info("If this is urgent, use the Emergency box below or call helplines.")

    # If last message was crisis, show emergency card
    # We inspect last logged event:
    cur.execute("SELECT detail, sentiment, is_crisis, ts FROM events ORDER BY id DESC LIMIT 1")
    last = cur.fetchone()
    if last:
        last_detail, last_sent, last_is_crisis, last_ts = last
        if last_is_crisis:
            st.markdown("## ⚠️ Immediate help recommended")
            st.error("We detected words or sentiment indicating high distress. Please consider the options below:")
            # show helplines
            st.markdown("- **Call local emergency/helpline now**")
            st.markdown("- **Trusted contact**: call or message them if you want (enter contact in sidebar)")
            if trusted_phone:
                st.markdown(f"[Call trusted contact] (tel:{trusted_phone})")
            if trusted_email:
                st.markdown(f"[Email trusted contact] (mailto:{trusted_email}?subject=Urgent%20Help&body=Please%20contact%20me%20ASAP.)")

            # option: send email to trusted contact if provided
            if trusted_email and st.button("Send Alert Email to Trusted Contact (with summary)"):
                summary = f"Automatic alert from MindCare prototype.\n\nMessage: {last_detail}\nSentiment: {last_sent}\nTime: {last_ts}\n\nPlease reach out to this person immediately."
                ok, msg = send_email_via_smtp(trusted_email, "MindCare Alert: Please check on your contact", summary)
                if ok:
                    st.success("Alert sent to trusted contact (via configured SMTP).")
                else:
                    st.warning(f"Could not send email: {msg}")

            # direct helpline links (India examples + global)
            st.markdown("**Immediate helplines**")
            st.markdown("- Vandrevala: 9152987821")
            st.markdown("- iCall: 9152987821")
            st.markdown("- International: see https://www.opencounseling.com/suicide-hotlines")

# ---------------------------
# Tab: Mood Tracker
# ---------------------------
with tabs[1]:
    st.header("Mood Tracker — track & share progress")
    # simple mood log
    if "mood_log" not in st.session_state:
        st.session_state["mood_log"] = []

    colA, colB = st.columns([3,1])
    with colA:
        mood = st.selectbox("How are you feeling right now?", ["Very Positive 😀", "Positive 🙂", "Neutral 😐", "Anxious 😟", "Very Negative 😢"])
        note = st.text_area("Optional note (private)")
        if st.button("Log today's mood"):
            mapping = {"Very Positive 😀":2, "Positive 🙂":1, "Neutral 😐":0, "Anxious 😟":-1, "Very Negative 😢":-2}
            score = mapping[mood]
            save_mood(mood, score, note or "")
            st.success("Mood logged — small steps matter.")
    with colB:
        if st.button("Download summary for clinician"):
            # create a plain text summary and offer as download
            df = pd.read_sql_query("SELECT * FROM moods ORDER BY id DESC LIMIT 50", conn)
            lines = ["MindCare — brief summary\n", f"Generated: {datetime.utcnow().isoformat()}\n", "Recent mood entries:\n"]
            for _, row in df.iterrows():
                lines.append(f"{row['ts']} | {row['mood_label']} | note: {row['note']}\n")
            txt = "\n".join(lines)
            st.download_button("Download summary (.txt)", txt, file_name="mindcare_summary.txt", mime="text/plain")

    # show chart
    dfm = get_moods_df()
    if not dfm.empty:
        dfm["ts_date"] = pd.to_datetime(dfm["ts"]).dt.date
        fig = px.line(dfm, x="ts_date", y="score", markers=True, title="Mood trend (score -2..2)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No mood data yet — encourage daily check-ins.")

# ---------------------------
# Tab: Resources & Connect
# ---------------------------
with tabs[2]:
    st.header("Resources & Connect")
    st.markdown("**Trusted resources**")
    st.markdown("- WHO mental health: https://www.who.int/health-topics/mental-health")
    st.markdown("- Crisis hotlines: see sidebar")

    st.markdown("---")
    st.subheader("Connect with local professionals (demo directory)")
    # demo mock directory — in real deployment you'd query an API / database
    providers = [
        {"name":"City Mental Health Clinic", "phone":"+91-11-1234-5678", "email":"clinic@example.com", "address":"Nearby St, City"},
        {"name":"University Counseling Centre", "phone":"+91-11-9999-0000", "email":"counsel@example.edu", "address":"Campus Rd"},
        {"name":"NGO Helpline", "phone":"+91-80-1111-2222", "email":"ngo@example.org", "address":"Community Center"}
    ]
    for p in providers:
        st.markdown(f"**{p['name']}**  \nAddress: {p['address']}  \nPhone: {p['phone']}  \nEmail: {p['email']}")
        # mailto booking button:
        mailto = f"mailto:{p['email']}?subject=Appointment%20Request%20from%20MindCare%20User&body=Hello%2C%0A%0AI%20would%20like%20to%20request%20an%20appointment.%20Please%20advise%20availability."
        if st.button(f"Request appointment — {p['name']}"):
            # either open mailto or send via SMTP if configured
            if st.secrets.get("smtp_user") or os.getenv("SMTP_USER"):
                # ask user for consent to share summary
                consent = st.checkbox("I consent to share my summary with this provider (demo)", key=f"consent_{p['name']}")
                if consent:
                    # build summary and send via SMTP
                    df = pd.read_sql_query("SELECT * FROM moods ORDER BY id DESC LIMIT 50", conn)
                    body_lines = [f"Appointment request from a MindCare user.\n\nRecent moods:\n"]
                    for _, r in df.iterrows():
                        body_lines.append(f"{r['ts']} | {r['mood_label']} | note: {r['note']}\n")
                    success, msg = send_email_via_smtp(p['email'], "MindCare: Appointment request", "\n".join(body_lines))
                    if success:
                        st.success("Appointment request sent (via configured SMTP).")
                    else:
                        st.error(f"Could not send: {msg}")
                else:
                    st.info("Please give consent to share your summary.")
            else:
                # fallback: open mailto
                st.markdown(f"[Open email client to request appointment]({mailto})")

    st.markdown("---")
    st.markdown("If you plan to connect with professionals, always ensure you consent to share personal notes. Data privacy is critical.")

# Footer
st.markdown("---")
st.caption("Demo prototype for educational use. Not a substitute for professional care.")

