




import streamlit as st
import requests
import time
from datetime import datetime
import pdfplumber
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()  # loads keys from .env
# =============================
# APP CONFIG
# =============================
st.set_page_config(
    page_title="MedAssist XR - AI Health Assistant",
    page_icon="🏥",
    layout="wide",
)

# =============================
# CUSTOM CSS
# =============================
st.markdown("""
<style>
    body {
        background-color: #f9fafc;
        color: #000000;
        font-family: 'Poppins', sans-serif;
    }

    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: white;
        text-align: center;
        background: linear-gradient(90deg, #0072ff, #00c6ff);
        padding: 1rem 0;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .sub-header {
        font-size: 1.2rem;
        color: #333333;
        text-align: center;
        margin-bottom: 2rem;
    }

    .chat-message {
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        color: #000;
        animation: fadeIn 0.5s;
    }

    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }

    .bot-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }

    .suggestion-chip {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        background-color: #0072ff;
        color: white;
        border-radius: 20px;
        cursor: pointer;
        font-size: 0.9rem;
        text-align: center;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .sidebar-section {
        background-color: #eef6ff;
        padding: 1rem;
        border-radius: 10px;
    }

    .feature-title {
        font-size: 1.1rem;
        font-weight: bold;
        margin-top: 1rem;
        color: #004aad;
    }

</style>
""", unsafe_allow_html=True)

# =============================
# SESSION STATE
# =============================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = []

# =============================
# CONFIG
# =============================
API_BASE_URL = "http://127.0.0.1:8000"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

# =============================
# HELPER FUNCTIONS
# =============================
def send_message(message: str):
    """Send message to FastAPI backend"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"message": message, "context": st.session_state.conversation_context},
            timeout=12
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"response": f"⚠️ Server Error ({response.status_code}). Try again later."}
    except requests.exceptions.ConnectionError:
        return {"response": "⚠️ Cannot connect to backend. Please ensure FastAPI is running."}
    except Exception as e:
        return {"response": f"⚠️ Error contacting backend: {e}"}

def analyze_report_with_groq(pdf_file):
    """Analyze uploaded medical report with Groq AI"""
    report_text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                report_text += text + "\n"

    if not report_text.strip():
        return "❌ Could not extract readable text from the PDF."

    prompt = f"""
    You are a professional medical assistant AI.
    Explain the following medical report in simple, human-understandable language.
    Identify abnormal values and give general health guidance (no medical diagnosis).

    Report:
    {report_text}
    """

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful medical report interpreter."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=800
    )

    return response.choices[0].message.content

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.markdown("<h2 style='color:#004aad;'>🏥 MedAssist XR</h2>", unsafe_allow_html=True)
    st.markdown("Your **AI Health Companion** for smarter, safer healthcare decisions.")
    st.markdown("---")

    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Features")
    st.markdown("""
    - 🩺 Symptom Analysis  
    - 📊 Lab Report Interpretation  
    - 👨‍⚕️ Doctor Finder  
    - 💊 Health Tips  
    - 📄 Medical Report Upload  
    """)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='feature-title'>👨‍⚕️ Find a Doctor</div>", unsafe_allow_html=True)
    st.info("🩺 This feature will be available in a few days.", icon="⏳")

    st.markdown("---")
    if st.button("🆕 New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_context = []
        st.rerun()

# =============================
# MAIN HEADER
# =============================
st.markdown("<div class='main-header'>MedAssist XR</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>AI-Powered Multimodal Health Assistant</div>", unsafe_allow_html=True)

# =============================
# CHAT CONTAINER
# =============================
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-message user-message'>👤 <b>You:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-message bot-message'>🤖 <b>MedAssist:</b><br>{msg['content']}</div>", unsafe_allow_html=True)

# =============================
# QUICK START SECTION
# =============================
if not st.session_state.messages:
    st.markdown("### 🚀 Quick Start")
    st.markdown("Choose an option below to begin interacting with MedAssist XR:")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🤒 Check Symptoms", use_container_width=True):
            user_input = "I have symptoms and need help"
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = send_message(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response["response"]})
            st.rerun()

    with col2:
        if st.button("📊 Explain Report", use_container_width=True):
            user_input = "I want to understand my lab report"
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = send_message(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response["response"]})
            st.rerun()

    with col3:
        if st.button("💡 Health Tips", use_container_width=True):
            user_input = "Give me some general health advice"
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = send_message(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response["response"]})
            st.rerun()

    with col4:
        uploaded_file = st.file_uploader("📄 Upload Medical Report", type=["pdf"])
        if uploaded_file:
            with st.spinner("Analyzing your report..."):
                result = analyze_report_with_groq(uploaded_file)
            st.session_state.messages.append({"role": "assistant", "content": result})
            st.rerun()

# =============================
# CHAT INPUT
# =============================
st.markdown("---")
user_input = st.chat_input("Type your health query or paste lab results here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("🤔 Thinking..."):
        response = send_message(user_input)
        time.sleep(0.5)
        st.session_state.messages.append({"role": "assistant", "content": response["response"]})
        st.session_state.conversation_context.append({
            "user": user_input,
            "assistant": response["response"],
            "timestamp": datetime.now().isoformat()
        })
    st.rerun()

# =============================
# FOOTER
# =============================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("🏥 **MedAssist XR v1.3**")
with col2:
    st.markdown("Made with ❤️ using **GROQ AI** & **Streamlit**")
with col3:
    st.markdown("🔒 Your health data stays private and secure.")
