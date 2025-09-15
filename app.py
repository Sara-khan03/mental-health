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


