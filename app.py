import streamlit as st
from textblob import TextBlob
import openai

# ==============================
# App Config
# ==============================
st.set_page_config(page_title="Mental Health Assistant",
                   page_icon="🌱",
                   layout="wide")

# ==============================
# Custom CSS
# ==============================
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ==============================
# Sidebar
# ==============================
st.sidebar.title("⚙️ Prototype Controls")
openai_api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

st.sidebar.markdown("---")
st.sidebar.info("🌍 **About this App**\n\nA supportive chatbot prototype for mental wellness, with mood tracking and resources.")

st.sidebar.markdown("---")
st.sidebar.error("🚨 **Emergency?**\n\nIf you’re in crisis, please call your local helpline immediately.")


# ---- Mood Tracker ----
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

if "mood_log" not in st.session_state:
    st.session_state["mood_log"] = []

st.sidebar.header("📝 Mood Tracker")

# Mood options
mood = st.sidebar.radio(
    "How are you feeling today?",
    ["😊 Happy", "😐 Neutral", "😢 Sad", "😡 Angry"]
)

if st.sidebar.button("Log Mood"):
    st.session_state["mood_log"].append(
        {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "mood": mood}
    )
    st.sidebar.success("Mood logged successfully ✅")

# Show mood history
if st.session_state["mood_log"]:
    df = pd.DataFrame(st.session_state["mood_log"])
    st.subheader("📊 Mood History")
    st.dataframe(df)

    # Plot mood counts
    st.subheader("📈 Mood Chart")
    fig, ax = plt.subplots()
    df["mood"].value_counts().plot(kind="bar", ax=ax, color="seagreen")
    ax.set_ylabel("Frequency")
    ax.set_xlabel("Mood")
    st.pyplot(fig)

# ==============================
# Main Layout with Tabs
# ==============================
st.title("🌱 Mental Health Assistant")
st.subheader("Your supportive AI companion for emotional well-being")

tabs = st.tabs(["💬 Chatbot", "📊 Mood Tracker", "📚 Resources"])

# ==============================
# Tab 1: Chatbot
# ==============================
with tabs[0]:
    st.header("💬 Chat with Me")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat history
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).markdown(msg["content"])

    # User input
    if user_input := st.chat_input("How are you feeling today?"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").markdown(user_input)

        # Fallback chatbot logic if no OpenAI key
        if not openai_api_key:
            analysis = TextBlob(user_input).sentiment.polarity
            if analysis > 0:
                response = "I'm glad to hear you're feeling positive 💙. Keep it up!"
            elif analysis < 0:
                response = "I'm sorry you're going through this 🌱. Remember, it's okay to feel this way."
            else:
                response = "Thanks for sharing. I'm here to listen whenever you need 💬."
        else:
            openai.api_key = openai_api_key
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a supportive mental health assistant."},
                    {"role": "user", "content": user_input}
                ]
            )
            response = completion.choices[0].message.content

        # Display response
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").markdown(response)

# ==============================
# Tab 2: Mood Tracker
# ==============================
with tabs[1]:
    st.header("📊 Mood Tracker")
    st.write("Mood tracking and graphs will be added here soon...")

# ==============================
# Tab 3: Resources
# ==============================
with tabs[2]:
    st.header("📚 Helpful Resources")
    st.markdown("""
    - 🌍 [WHO Mental Health Resources](https://www.who.int/health-topics/mental-health)
    - 📞 [Find a Helpline](https://findahelpline.com/)
    - 📖 Self-care tips: Take breaks, stay active, talk to someone you trust.
    """)

