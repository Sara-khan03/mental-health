# app.py
# MindCare prototype - Chatbot + Mood Tracker + Crisis Detection + Connect to Professionals
# Run: python -m streamlit run app.py

# app.py
# Streamlit prototype: Digital Mental Health MVP
# Run: pip install -r requirements.txt
#      streamlit run app.py

import streamlit as st

# ========================
# CONFIG
# ========================
st.set_page_config(
    page_title="MindCare - Mental Health Support",
    page_icon="🧠",
    layout="wide"
)

# Load custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ========================
# DATABASE (India + USA sample)
# ========================
psychiatrists_db = {
    "India": {
        "Delhi": [
            {"name": "Dr. Samir Parikh", "hospital": "Fortis Hospital, Delhi", "contact": "+91-9811111111"},
            {"name": "Dr. Nand Kumar", "hospital": "AIIMS Delhi", "contact": "+91-9811222222"},
        ],
        "Maharashtra": [
            {"name": "Dr. Anjali Chhabria", "hospital": "Mindtemple Clinic, Mumbai", "contact": "+91-9820000000"},
            {"name": "Dr. Harish Shetty", "hospital": "L H Hiranandani Hospital, Mumbai", "contact": "+91-9820111111"},
        ],
    },
    "USA": {
        "California": [
            {"name": "Dr. Laura Smith", "hospital": "Stanford Hospital, Palo Alto", "contact": "+1-650-123-4567"},
            {"name": "Dr. John Doe", "hospital": "UCLA Medical Center, Los Angeles", "contact": "+1-310-987-6543"},
        ],
        "New York": [
            {"name": "Dr. Emily Carter", "hospital": "NYU Langone, New York", "contact": "+1-212-333-4444"},
            {"name": "Dr. Michael Johnson", "hospital": "Mount Sinai Hospital, New York", "contact": "+1-212-555-6666"},
        ],
    }
}

# ========================
# NAVIGATION
# ========================
menu = ["🏠 Home", "💬 Chatbot", "🧑‍⚕️ Find Psychiatrists",
        "📚 Resources", "🚨 Emergency", "ℹ️ About"]

choice = st.sidebar.radio("Navigate", menu)

# ========================
# PAGES
# ========================

# ---- HOME ----
if choice == "🏠 Home":
    st.title("🏠 Welcome to MindCare")
    st.markdown("""
    Your trusted companion for **mental health awareness & support**.  

    ### What you can do here:
    - Talk to a **mental health chatbot** 🤖  
    - Find **psychiatrists near you** (India + USA) 🧑‍⚕️  
    - Access **resources and self-help guides** 📚  
    - Get **emergency support instantly** 🚨  
    """)

# ---- CHATBOT ----
elif choice == "💬 Chatbot":
    st.title("💬 Chatbot Support")
    user_input = st.text_input("How are you feeling today?")

    if st.button("Submit") and user_input:
        if "suicide" in user_input.lower() or "kill myself" in user_input.lower():
            st.error("🚨 Urgent! If you're in danger, call emergency immediately.")
            st.warning("👉 Go to Emergency Page from sidebar.")
        elif "stress" in user_input.lower() or "anxiety" in user_input.lower():
            st.info("😟 It sounds like you're stressed. Try this simple exercise:")
            st.markdown("""
            **🌬️ Breathing Exercise (2 min)**
            1. Inhale deeply for 4 seconds  
            2. Hold for 7 seconds  
            3. Exhale slowly for 8 seconds  
            Repeat this 4 times.
            """)
        else:
            st.success("💙 Thank you for sharing. Talking is the first step towards healing.")

# ---- PSYCHIATRISTS ----
elif choice == "🧑‍⚕️ Find Psychiatrists":
    st.title("🧑‍⚕️ Find Psychiatrists Near You")

    country = st.selectbox("🌍 Select Country", list(psychiatrists_db.keys()))
    if country:
        state = st.selectbox("📍 Select State", list(psychiatrists_db[country].keys()))

        if state:
            doctors = psychiatrists_db[country][state]
            for d in doctors:
                st.markdown(f"""
                <div class="card">
                    <h4>{d['name']}</h4>
                    <p>🏥 {d['hospital']}</p>
                    <p>📞 {d['contact']}</p>
                </div>
                """, unsafe_allow_html=True)

# ---- RESOURCES ----
elif choice == "📚 Resources":
    st.title("📚 Self-Help Resources")
    st.markdown("""
    - 🌍 [WHO Mental Health Resources](https://www.who.int/health-topics/mental-health)  
    - 🧘 [Headspace Meditation App](https://www.headspace.com/)  
    - 🎓 [Coursera - Mental Health Courses](https://www.coursera.org/)  
    - 🎓 [Udemy - Psychology & Mental Wellness](https://www.udemy.com/)  
    """)

# ---- EMERGENCY ----
elif choice == "🚨 Emergency":
    st.title("🚨 Emergency & Helplines")

    st.subheader("📞 India")
    st.write("AASRA Suicide Helpline: **+91-9152987821**")
    st.write("Snehi Mental Health Helpline: **+91-022-27546669**")

    st.subheader("📞 USA")
    st.write("Suicide & Crisis Lifeline: **988**")
    st.write("SAMHSA Mental Health: **1-800-662-HELP (4357)**")

# ---- ABOUT ----
elif choice == "ℹ️ About":
    st.title("ℹ️ About MindCare")
    st.markdown("""
    **Disclaimer:**  
    This app provides mental health awareness and resources.  
    It is **not a substitute for professional medical advice**.  
    Always consult a licensed doctor or psychiatrist for serious concerns.  
    """)
