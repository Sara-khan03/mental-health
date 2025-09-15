# app.py
# MindCare prototype - Chatbot + Mood Tracker + Crisis Detection + Connect to Professionals
# Run: python -m streamlit run app.py

# app.py
# Streamlit prototype: Digital Mental Health MVP
# Run: pip install -r requirements.txt
#      streamlit run app.py


import os
import sqlite3
from datetime import datetime, date
import textwrap
import streamlit as st
from textblob import TextBlob
import openai
import plotly.express as px
import pandas as pd

# -------------------------
# Config / DB helpers
# -------------------------
DB_PATH = "mh_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    # chats: id, role ('user'/'bot'), text, sentiment, ts
    cur.execute("""CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    text TEXT,
                    sentiment REAL,
                    ts TEXT
                )""")
    # moods: id, mood_label, score (-2..2), note, ts
    cur.execute("""CREATE TABLE IF NOT EXISTS moods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mood_label TEXT,
                    score INTEGER,
                    note TEXT,
                    ts TEXT
                )""")
    # points (wellness gamification)
    cur.execute("""CREATE TABLE IF NOT EXISTS points (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reason TEXT,
                    points INTEGER,
                    ts TEXT
                )""")
    conn.commit()
    return conn

conn = init_db()
cur = conn.cursor()

# -------------------------
# Utilities
# -------------------------
def save_chat(role, text, sentiment):
    ts = datetime.utcnow().isoformat()
    cur.execute("INSERT INTO chats (role, text, sentiment, ts) VALUES (?, ?, ?, ?)",
                (role, text[:2000], sentiment, ts))
    conn.commit()

def get_chats(limit=200):
    cur.execute("SELECT role, text, sentiment, ts FROM chats ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    return [{"role": r[0], "text": r[1], "sentiment": r[2], "ts": r[3]} for r in rows][::-1]

def save_mood(label, score, note=""):
    ts = datetime.utcnow().isoformat()
    cur.execute("INSERT INTO moods (mood_label, score, note, ts) VALUES (?, ?, ?, ?)",
                (label, score, note[:1000], ts))
    conn.commit()

def get_moods():
    cur.execute("SELECT mood_label, score, note, ts FROM moods ORDER BY id ASC")
    rows = cur.fetchall()
    return [{"mood":r[0], "score":r[1], "note":r[2], "ts":r[3]} for r in rows]

def add_points(reason, pts):
    ts = datetime.utcnow().isoformat()
    cur.execute("INSERT INTO points (reason, points, ts) VALUES (?, ?, ?)", (reason, pts, ts))
    conn.commit()

def get_points_total():
    cur.execute("SELECT SUM(points) FROM points")
    s = cur.fetchone()[0]
    return int(s or 0)

# -------------------------
# Chatbot: OpenAI or fallback
# -------------------------
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_KEY:
    openai.api_key = OPENAI_KEY

CRISIS_KEYWORDS = ["suicide", "kill myself", "end my life", "hurt myself", "want to die", "can't go on", "killme"]

def analyze_sentiment(text: str):
    try:
        blob = TextBlob(text)
        return round(blob.sentiment.polarity, 3)
    except Exception:
        return 0.0

def detect_crisis(text: str, sentiment: float):
    txt = text.lower()
    if any(k in txt for k in CRISIS_KEYWORDS):
        return True
    if sentiment <= -0.6:
        return True
    return False

def generate_bot_reply(user_text: str):
    # Primary: OpenAI (if key set)
    if OPENAI_KEY:
        try:
            prompt_system = ("You are a supportive, empathetic mental health assistant for students. "
                             "Use short, clear sentences. If the user expresses self-harm intent, provide crisis resources and advise to contact emergency help.")
            messages = [
                {"role":"system","content":prompt_system},
                {"role":"user","content":user_text}
            ]
            resp = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=300, temperature=0.7)
            reply = resp.choices[0].message.content.strip()
            return reply
        except Exception as e:
            # fallback to rule-based
            pass

    # Fallback rule-based empathetic reply
    txt = user_text.lower()
    if any(k in txt for k in ["stress","stressed","anxious","anxiety","panic"]):
        return ("I'm sorry you're feeling stressed — that sounds tough. "
                "Would you like a short breathing exercise or some tips to handle an upcoming deadline?")
    if any(k in txt for k in ["sad","depressed","down","hopeless"]):
        return ("I hear you. Feeling low is valid. Can you tell me one small thing that felt okay today?")
    if any(k in txt for k in ["sleep","insomnia","can't sleep","tired"]):
        return ("Sleep problems can make everything harder. Try a 4-4-4 breathing before bed and reduce screen time an hour before sleep.")
    return ("Thanks for sharing. Tell me more, or choose 'Self-care' for exercises that may help right now.")

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="MindCare MVP", layout="wide", page_icon="🧠")
st.markdown("<style>footer{visibility:hidden;} </style>", unsafe_allow_html=True)

# attempt to load external css if present
if os.path.exists("styles.css"):
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("MindCare — Digital Mental Health (Prototype)")
st.markdown("Calm demo of chatbot, mood tracker, self-care and dashboard (MVP).")

# Layout: sidebar for navigation / meta
with st.sidebar:
    st.header("Prototype Controls")
    if OPENAI_KEY:
        st.success("OpenAI available — chatbot powered by GPT")
    else:
        st.info("No OpenAI key — using fallback rule-based chatbot")
    st.markdown("---")
    if st.button("Reset all data (DB)"):
        conn.close()
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        st.experimental_rerun()
    st.markdown("**Wellness points:** " + str(get_points_total()))

tabs = st.tabs(["Home", "Chatbot", "Mood Tracker", "Self-care", "Dashboard"])

# -------------------------
# Home tab
# -------------------------
with tabs[0]:
    st.header("Welcome")
    st.markdown("""
    **MindCare (MVP)** helps students log mood, get instant empathetic chat support, and track well-being.
    *This prototype is for demo & hackathon use — not a substitute for professional medical care.*
    """)
    st.info("Tip: Use the Chatbot tab to test conversation. Log moods in Mood Tracker. See trends in Dashboard.")

# -------------------------
# Chatbot tab
# -------------------- Chatbot Page --------------------
# -------------------- Chatbot --------------------
elif page == "Chatbot":
    st.title("💬 Mental Health Chatbot")

    # Initialize session state safely
    if "chat_input" not in st.session_state:
        st.session_state["chat_input"] = ""

    st.write("Select a quick prompt or type how you are feeling:")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("😟 Stressed about exams"):
            st.session_state["chat_input"] = "I am stressed about exams and can't focus."
    with col2:
        if st.button("😊 Feeling happy"):
            st.session_state["chat_input"] = "I am feeling very happy and motivated today!"
    with col3:
        if st.button("😔 Feeling lonely"):
            st.session_state["chat_input"] = "I am feeling lonely and need some advice."

    # Text input linked to session state
    user_input = st.text_input("Explain how you are feeling:", key="chat_input")

    # Show chatbot response
    if user_input:
        st.write(f"🧑‍⚕️ You said: {user_input}")

        if "stressed" in user_input.lower():
            st.info("💡 Tip: Take a 5-minute break, practice deep breathing, and try to focus on one task at a time.")
        elif "happy" in user_input.lower():
            st.success("🌟 That's amazing! Keep doing what makes you happy and spread positivity.")
        elif "lonely" in user_input.lower():
            st.warning("🤝 You’re not alone. Try calling a close friend or joining a community activity.")
        else:
            st.info("🧠 Remember, it's okay to talk about your feelings. Keep expressing yourself.")

# -------------------------
# Mood Tracker
# -------------------------
with tabs[2]:
    st.header("Mood Tracker 📊")
    st.markdown("Log how you're feeling. Visualize trends over time. Small, consistent tracking helps detect early changes.")

    # mood input
    colA, colB = st.columns([2,1])
    with colA:
        mood = st.selectbox("Today's mood", ["Very Positive 😀", "Positive 🙂", "Neutral 😐", "Anxious 😟", "Very Negative 😢"])
        note = st.text_area("Short note (optional, private)", max_chars=300)
    with colB:
        if st.button("Log Mood"):
            mapping = {"Very Positive 😀":2, "Positive 🙂":1, "Neutral 😐":0, "Anxious 😟":-1, "Very Negative 😢":-2}
            score = mapping[mood]
            save_mood(mood, score, note or "")
            add_points("Log mood", 5)
            st.success("Mood logged. Thank you — small actions add up!")
            st.experimental_rerun()

    # show recent moods chart
    moods = get_moods()
    if moods:
        df = pd.DataFrame(moods)
        df["ts_date"] = pd.to_datetime(df["ts"]).dt.date
        fig = px.line(df, x="ts_date", y="score", markers=True, title="Mood trend (score -2..2)")
        fig.update_layout(yaxis=dict(dtick=1))
        st.plotly_chart(fig, use_container_width=True)
        st.table(df.tail(6)[["ts","mood","note"]])
    else:
        st.info("No moods logged yet. Encourage users to log daily.")

# -------------------------
# Self-care
# -------------------------
with tabs[3]:
    st.header("Self-care exercises & micro-tasks 🧘")
    st.markdown("Short practices to reduce stress and build resilience. Earn wellness points for completing activities.")

    if st.button("3-minute breathing exercise (4-4-4)"):
        add_points("Breathing exercise", 10)
        st.success("Nice! +10 points — try the breathing cycle: inhale 4s, hold 4s, exhale 4s. Repeat 6 times.")

    if st.button("1-minute grounding"):
        add_points("Grounding", 5)
        st.success("Nice! +5 points — look around, name 5 things you can see, 4 you can touch.")

    if st.button("Write a gratitude sentence"):
        add_points("Gratitude", 5)
        st.success("Nice! +5 points — being grateful boosts mood.")

    st.markdown("**Wellness Points**: " + str(get_points_total()))

# -------------------------
# Dashboard
# -------------------------
with tabs[4]:
    st.header("Student Dashboard — Snapshot")
    st.markdown("Personalized view: mood trend, recent chat sentiment, wellness points")

    # mood trend (recent)
    moods = get_moods()
    if moods:
        df = pd.DataFrame(moods)
        df["ts_date"] = pd.to_datetime(df["ts"]).dt.date
        fig = px.bar(df, x="ts_date", y="score", title="Mood bars (recent entries)", labels={"score":"mood score"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No mood data yet — use the Mood Tracker tab")

    # recent chat sentiment summary
    chats = get_chats(30)
    if chats:
        chat_df = pd.DataFrame(chats)
        chat_df = chat_df[chat_df["role"]=="user"]
        avg_sent = chat_df["sentiment"].mean()
        st.metric("Average recent sentiment", f"{avg_sent:.2f}")
        st.table(chat_df.tail(6)[["ts","text","sentiment"]])
    else:
        st.info("No chat history yet.")

    st.markdown("**Total wellness points:** " + str(get_points_total()))

# Footer / note
st.markdown("---")
st.caption("Prototype for demo only — this is not a clinical tool. For real emergencies contact local services.")




