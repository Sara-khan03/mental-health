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

import streamlit as st

# Sidebar navigation
st.sidebar.title("Mental Health App")
page = st.sidebar.radio("Navigate", ["Home", "Resources", "Chatbot"])

# -------------------- Home --------------------
if page == "Home":
    st.title("🏠 Welcome to the Mental Health Support App")
    st.write(
        "This app helps you express your feelings and get helpful suggestions, "
        "including relaxation techniques, resources, and professional support contacts."
    )

# -------------------- Resources --------------------
elif page == "Resources":
    st.title("📚 Resources")
    st.write("Here are some important mental health helplines and resources:")

    st.info("🇮🇳 India Helpline: Vandrevala Foundation Helpline – 1860 266 2345 or 1800 233 3330")
    st.info("🇺🇸 USA Helpline: National Suicide Prevention Lifeline – 988")
    st.info("🌍 International: https://findahelpline.com")

# -------------------- Chatbot --------------------
elif page == "Chatbot":
    st.title("💬 Mental Health Chatbot")
    st.write("Select a quick prompt or type how you are feeling:")

    # Initialize session state safely
    if "chat_input" not in st.session_state:
        st.session_state["chat_input"] = ""

    # Quick prompt buttons
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

    # User input box
    user_input = st.text_input("📝 Explain how you are feeling:", key="chat_input")

    # Chatbot response
    if user_input:
        st.write(f"🧑‍⚕️ You said: {user_input}")

        text = user_input.lower()

        # Conditions
        if any(word in text for word in ["stress", "exam", "tension", "focus"]):
            st.warning("😟 It sounds like you're stressed. Try this quick exercise:")
            st.info("👉 Close your eyes. Inhale deeply for 4 seconds, hold for 7 seconds, exhale for 8 seconds. Repeat 3 times.")
            st.write("📞 If stress feels overwhelming, consider reaching out to a counselor or helpline.")

        elif any(word in text for word in ["anxious", "anxiety", "panic"]):
            st.warning("😰 You're feeling anxious. Try grounding yourself:")
            st.info("👉 5-4-3-2-1 method: Name 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste.")
            st.write("📞 Professional support can really help — try contacting a mental health professional.")

        elif any(word in text for word in ["sad", "lonely", "depressed", "alone"]):
            st.warning("😔 You're not alone in this. Here’s something that may help:")
            st.info("👉 Call a trusted friend or family member. Journaling your feelings may also help.")
            st.error("⚠️ If sadness feels too heavy, please call a helpline immediately (India: 1800 233 3330, USA: 988).")

        elif any(word in text for word in ["suicide", "kill myself", "end my life"]):
            st.error("🚨 This is very serious. Your life matters.")
            st.error("📞 Please call a suicide prevention helpline IMMEDIATELY:")
            st.write("🇮🇳 India: Vandrevala Helpline – 1860 266 2345 / 1800 233 3330")
            st.write("🇺🇸 USA: National Suicide Prevention Lifeline – 988")
            st.write("🌍 Global directory: https://findahelpline.com")

        elif "happy" in text or "excited" in text:
            st.success("🌟 That’s amazing! Keep doing what makes you happy.")
            st.info("👉 Try sharing your positive energy — maybe call a friend or write down what you’re grateful for.")

        else:
            st.info("🧠 Thank you for sharing your feelings. It’s good to express yourself.")
            st.write("👉 If you want, you can also check the **Resources** page for professional support.")

# psychiatrist_db_module.py
import streamlit as st
import urllib.parse

# ---------------------------
# Expanded Psychiatry / Mental-Health Resource DB
# ---------------------------
# NOTE: This DB mixes (a) widely-public helplines, (b) a few well-known hospital contacts,
# and (c) placeholders for state-level entries. Replace placeholders with real local data
# or connect to a live API (Google Places / Healthgrades / Practo / local health dept).
#
# Each entry: { "name", "type": ("hospital"/"clinic"/"helpline"/"private"), "phone", "address", "city", "state", "telehealth_url", "notes" }

INDIA_STATE_RESOURCES = {
    "Andhra Pradesh": [
        {"name":"State Mental Health Helpline (Andhra Pradesh)", "type":"helpline", "phone":"1800-000-000", "address":"State Health Dept", "city":"Amaravati", "state":"Andhra Pradesh", "telehealth_url":"", "notes":"Replace with state helpline"}
    ],
    "Arunachal Pradesh":[
        {"name":"State Mental Health Helpline (Arunachal)", "type":"helpline", "phone":"1800-000-001", "address":"Itanagar", "city":"Itanagar", "state":"Arunachal Pradesh", "telehealth_url":"", "notes":""}
    ],
    "Assam":[
        {"name":"Gauhati Medical College (Psychiatry dept)", "type":"hospital", "phone":"+91-361-1234567", "address":"Guwahati, Assam", "city":"Guwahati", "state":"Assam", "telehealth_url":"", "notes":"Contact hospital psychiatry department"}
    ],
    "Bihar":[
        {"name":"State Mental Health Helpline (Bihar)", "type":"helpline", "phone":"1800-000-002", "address":"Patna", "city":"Patna", "state":"Bihar", "telehealth_url":"", "notes":""}
    ],
    "Chhattisgarh":[
        {"name":"All India Institute of Medical Sciences Raipur (Psychiatry)", "type":"hospital", "phone":"+91-771-2985000", "address":"AIIMS Raipur, Tatibandh", "city":"Raipur", "state":"Chhattisgarh", "telehealth_url":"", "notes":"Example contact, verify before use"}
    ],
    "Goa":[
        {"name":"Goa State Mental Health Helpline", "type":"helpline", "phone":"1800-000-003", "address":"Panaji", "city":"Panaji", "state":"Goa", "telehealth_url":"", "notes":""}
    ],
    "Gujarat":[
        {"name":"Gujarat State Mental Health Helpline", "type":"helpline", "phone":"1800-000-004", "address":"Gandhinagar", "city":"Gandhinagar", "state":"Gujarat", "telehealth_url":"", "notes":""}
    ],
    "Haryana":[
        {"name":"PGIMS Rohtak Psychiatry", "type":"hospital", "phone":"+91-1262-123456", "address":"Rohtak", "city":"Rohtak", "state":"Haryana", "telehealth_url":"", "notes":""}
    ],
    "Himachal Pradesh":[
        {"name":"Himachal State Mental Health Helpline", "type":"helpline", "phone":"1800-000-005", "address":"Shimla", "city":"Shimla", "state":"Himachal Pradesh", "telehealth_url":"", "notes":""}
    ],
    "Jharkhand":[
        {"name":"Ranchi Institute Psychiatry", "type":"hospital", "phone":"1800-000-006", "address":"Ranchi", "city":"Ranchi", "state":"Jharkhand", "telehealth_url":"", "notes":""}
    ],
    "Karnataka":[
        {"name":"NIMHANS (Bengaluru) - National Institute of Mental Health & Neuro Sciences", "type":"hospital", "phone":"+91-80-26995100", "address":"Bengaluru", "city":"Bengaluru", "state":"Karnataka", "telehealth_url":"", "notes":"Top mental health institute in India"}
    ],
    "Kerala":[
        {"name":"Kerala State Mental Health Helpline", "type":"helpline", "phone":"1800-000-007", "address":"Thiruvananthapuram", "city":"Thiruvananthapuram", "state":"Kerala", "telehealth_url":"", "notes":""}
    ],
    "Madhya Pradesh":[
        {"name":"Madhya Pradesh State Mental Health Helpline", "type":"helpline", "phone":"1800-000-008", "address":"Bhopal", "city":"Bhopal", "state":"Madhya Pradesh", "telehealth_url":"", "notes":""}
    ],
    "Maharashtra":[
        {"name":"KEM Hospital Psychiatry (Mumbai)", "type":"hospital", "phone":"+91-22-2413-0000", "address":"Mumbai", "city":"Mumbai", "state":"Maharashtra", "telehealth_url":"", "notes":"Verify numbers before publishing"}
    ],
    "Manipur":[
        {"name":"Manipur State Mental Health Helpline", "type":"helpline", "phone":"1800-000-009", "address":"Imphal", "city":"Imphal", "state":"Manipur", "telehealth_url":"", "notes":""}
    ],
    "Meghalaya":[
        {"name":"Meghalaya State Mental Health Helpline", "type":"helpline", "phone":"1800-000-010", "address":"Shillong", "city":"Shillong", "state":"Meghalaya", "telehealth_url":"", "notes":""}
    ],
    "Mizoram":[
        {"name":"Mizoram State Mental Health Helpline", "type":"helpline", "phone":"1800-000-011", "address":"Aizawl", "city":"Aizawl", "state":"Mizoram", "telehealth_url":"", "notes":""}
    ],
    "Nagaland":[
        {"name":"Nagaland State Mental Health Helpline", "type":"helpline", "phone":"1800-000-012", "address":"Kohima", "city":"Kohima", "state":"Nagaland", "telehealth_url":"", "notes":""}
    ],
    "Odisha":[
        {"name":"SCB Medical College Psychiatry (Cuttack)", "type":"hospital", "phone":"+91-671-2300050", "address":"Cuttack", "city":"Cuttack", "state":"Odisha", "telehealth_url":"", "notes":""}
    ],
    "Punjab":[
        {"name":"PGIMER Psychiatry (Chandigarh region)", "type":"hospital", "phone":"+91-172-275-6666", "address":"Chandigarh", "city":"Chandigarh", "state":"Punjab", "telehealth_url":"", "notes":""}
    ],
    "Rajasthan":[
        {"name":"Rajasthan State Mental Health Helpline", "type":"helpline", "phone":"1800-000-013", "address":"Jaipur", "city":"Jaipur", "state":"Rajasthan", "telehealth_url":"", "notes":""}
    ],
    "Sikkim":[
        {"name":"Sikkim State Mental Health Helpline", "type":"helpline", "phone":"1800-000-014", "address":"Gangtok", "city":"Gangtok", "state":"Sikkim", "telehealth_url":"", "notes":""}
    ],
    "Tamil Nadu":[
        {"name":"Government Mental Health Clinic (Chennai)", "type":"hospital", "phone":"+91-44-12345678", "address":"Chennai", "city":"Chennai", "state":"Tamil Nadu", "telehealth_url":"", "notes":""}
    ],
    "Telangana":[
        {"name":"Institute of Mental Health (Erragadda, Hyderabad)", "type":"hospital", "phone":"+91-40-2354-XXXX", "address":"Hyderabad", "city":"Hyderabad", "state":"Telangana", "telehealth_url":"", "notes":"Replace X with actual digits"}
    ],
    "Tripura":[
        {"name":"Tripura State Mental Health Helpline", "type":"helpline", "phone":"1800-000-015", "address":"Agartala", "city":"Agartala", "state":"Tripura", "telehealth_url":"", "notes":""}
    ],
    "Uttar Pradesh":[
        {"name":"King George's Medical University Psychiatry (Lucknow)", "type":"hospital", "phone":"+91-522-2740000", "address":"Lucknow", "city":"Lucknow", "state":"Uttar Pradesh", "telehealth_url":"", "notes":""}
    ],
    "Uttarakhand":[
        {"name":"Uttarakhand State Mental Health Helpline", "type":"helpline", "phone":"1800-000-016", "address":"Dehradun", "city":"Dehradun", "state":"Uttarakhand", "telehealth_url":"", "notes":""}
    ],
    "West Bengal":[
        {"name":"S. K. B. Medical College Psychiatry (Howrah/Kolkata)", "type":"hospital", "phone":"+91-33-12345678", "address":"Kolkata", "city":"Kolkata", "state":"West Bengal", "telehealth_url":"", "notes":""}
    ],
    # UTs and Others
    "Andaman & Nicobar": [{"name":"A&N Mental Health Helpline","type":"helpline","phone":"1800-000-017","address":"Port Blair","city":"Port Blair","state":"Andaman & Nicobar","telehealth_url":"","notes":""}],
    "Chandigarh": [{"name":"Chandigarh Mental Health Helpline","type":"helpline","phone":"1800-000-018","address":"Chandigarh","city":"Chandigarh","state":"Chandigarh","telehealth_url":"","notes":""}],
    "Dadra and Nagar Haveli": [{"name":"DNH Helpline","type":"helpline","phone":"1800-000-019","address":"Dadra","city":"Dadra","state":"Dadra and Nagar Haveli","telehealth_url":"","notes":""}],
    "Daman & Diu": [{"name":"Daman Helpline","type":"helpline","phone":"1800-000-020","address":"Daman","city":"Daman","state":"Daman & Diu","telehealth_url":"","notes":""}],
    "Delhi": [
        {"name":"AIIMS Delhi Psychiatry", "type":"hospital", "phone":"+91-11-2658-8500", "address":"AIIMS, New Delhi", "city":"New Delhi", "state":"Delhi", "telehealth_url":"", "notes":""},
        {"name":"Delhi Mental Health Helpline", "type":"helpline", "phone":"1860-266-2345", "address":"Delhi", "city":"New Delhi", "state":"Delhi", "telehealth_url":"", "notes":"Vandrevala/other national helpline"}
    ],
    "Lakshadweep": [{"name":"Lakshadweep Helpline","type":"helpline","phone":"1800-000-021","address":"Kavaratti","city":"Kavaratti","state":"Lakshadweep","telehealth_url":"","notes":""}],
    "Puducherry": [{"name":"Puducherry Helpline","type":"helpline","phone":"1800-000-022","address":"Puducherry","city":"Puducherry","state":"Puducherry","telehealth_url":"","notes":""}],
}

# USA minimal DB - federal plus state placeholders (use 988 as national helpline)
USA_STATE_RESOURCES = {
    "national": [
        {"name":"US National Suicide & Crisis Lifeline", "type":"helpline", "phone":"988", "address":"USA", "city":"Nationwide", "state":"USA", "telehealth_url":"https://988lifeline.org", "notes":"Dial 988 for immediate support"}
    ]
}

# Create placeholders for US states
US_STATES = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","Florida",
             "Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine",
             "Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska",
             "Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota",
             "Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee",
             "Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]

for s in US_STATES:
    USA_STATE_RESOURCES[s] = [
        {"name": f"{s} State Mental Health Hotline (placeholder)", "type":"helpline", "phone":"988", "address":s, "city":s, "state":s, "telehealth_url":"https://www.samhsa.gov/find-help/national-helpline", "notes":"Replace with state/local resources"}
    ]

# ---------------------------
# Helper functions
# ---------------------------
def normalize(s: str) -> str:
    return s.strip().lower() if isinstance(s, str) else ""

def search_resources_by_location(query: str, country_hint: str = "India"):
    """
    Query can be city or state or 'psychiatrist in <city>'.
    country_hint: 'India' or 'USA' - used to search the appropriate DB first.
    Returns list of matches.
    """
    q = normalize(query)
    matches = []

    # check India DB
    for state, items in INDIA_STATE_RESOURCES.items():
        if q == normalize(state) or q in normalize(state) or normalize(state) in q:
            matches.extend(items)
        else:
            # also check cities inside each entry
            for e in items:
                if q == normalize(e.get("city", "")) or q in normalize(e.get("city", "")):
                    matches.append(e)

    # check USA DB if not found and country_hint is USA
    if not matches and (country_hint.lower() in ["usa","us","united states","america"] or "usa" in q or "us" in q):
        for state, items in USA_STATE_RESOURCES.items():
            if normalize(state) in q or q == normalize(state):
                matches.extend(items)
            else:
                for e in items:
                    if q == normalize(e.get("city","")) or q in normalize(e.get("city","")):
                        matches.append(e)

    # If still none, fallback to national helplines
    if not matches:
        # If query contains a US city/state keyword heuristics: return USA national
        if any(tok in q for tok in ["usa","us","united states","new york","san francisco","los angeles","chicago"]):
            matches.extend(USA_STATE_RESOURCES["national"])
        else:
            # default India national helpline + Delhi AIIMS if query empty
            matches.extend(INDIA_STATE_RESOURCES.get("Delhi", []))
            matches.append({"name":"National Mental Health Helpline (India) - Vandrevala or similar", "type":"helpline", "phone":"1860-266-2345", "address":"Nationwide", "city":"Nationwide", "state":"India", "telehealth_url":"", "notes":"Replace with the country's official helpline as appropriate"})

    return matches

def google_maps_link(address: str, name: str = "") -> str:
    q = f"{name} {address}".strip()
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(q)

def make_vcard(entry):
    """Return vCard string for download (basic)."""
    name = entry.get("name", "Contact")
    phone = entry.get("phone", "")
    org = entry.get("address", "")
    vcard = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{name}",
        f"FN:{name}",
        f"ORG:{org}",
        f"TEL;TYPE=WORK,VOICE:{phone}",
        "END:VCARD"
    ]
    return "\n".join(vcard)

# ---------------------------
# Streamlit UI snippet to integrate
# ---------------------------
def show_psychiatrist_search_ui():
    st.header("Find Mental Health Support — Search by city/state")
    col1, col2 = st.columns([3,1])
    with col1:
        query = st.text_input("Search (e.g., 'psychiatrist in delhi', 'hyderabad', 'california')", value="")
    with col2:
        country = st.selectbox("Country", ["India", "USA"], index=0)

    if st.button("Search"):
        if not query.strip():
            st.warning("Please enter a city or state (e.g., 'delhi', 'bengaluru', 'california').")
            return
        results = search_resources_by_location(query, country_hint=country)
        st.success(f"Found {len(results)} resource(s) — verify details before contact.")
        for r in results:
            st.markdown("**" + r.get("name", "Unknown") + "**")
            st.write(f"- Type: {r.get('type','')}")
            st.write(f"- Phone: {r.get('phone','N/A')}")
            st.write(f"- Address: {r.get('address','N/A')}, City: {r.get('city','N/A')}, State: {r.get('state','N/A')}")
            if r.get("telehealth_url"):
                st.markdown(f"- [Book Teleconsult]({r.get('telehealth_url')})")
            # Google maps
            maps_url = google_maps_link(r.get("address","") + " " + r.get("city",""))
            st.markdown(f"- [View on Google Maps]({maps_url})")
            # vCard download
            vcard = make_vcard(r)
            b64 = vcard.encode("utf-8").decode("latin1")
            btn_key = f"vcard_{r.get('name','')}"
            st.download_button(label="Download contact (vCard)", data=vcard, file_name=f"{r.get('name','contact')}.vcf", mime="text/vcard")
            st.markdown("---")

    # Quick emergency panel
    st.subheader("Emergency & Immediate Help")
    st.warning("If you or someone is in immediate danger or thinking about self-harm, call emergency services now.")
    st.write("- India national helpline (example): 1860 266 2345")
    st.write("- USA national helpline: 988")
    st.info("When in doubt, call local emergency services (police/ambulance) or a national crisis helpline.")

# If you want to test this module standalone:
if __name__ == "__main__":
    st.title("Psychiatrist / Mental Health Resources Module (Demo)")
    show_psychiatrist_search_ui()


