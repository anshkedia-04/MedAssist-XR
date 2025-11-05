import streamlit as st
import requests
import time
from datetime import datetime
import pdfplumber
from groq import Groq
from dotenv import load_dotenv
import os


load_dotenv()

# =============================
# APP CONFIG
# =============================
st.set_page_config(
    page_title="MedAssist XR - AI Health Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================
# COLORFUL CUSTOM CSS - VIBRANT HEALTHCARE UI
# =============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 50%, #80cbc4 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }
    
    /* ===== HERO HEADER ===== */
    .hero-header {
        background: linear-gradient(135deg, #00796b 0%, #00acc1 50%, #0288d1 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 15px 50px rgba(0, 121, 107, 0.3);
        position: relative;
        overflow: hidden;
        border: 3px solid rgba(255, 255, 255, 0.2);
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        border-radius: 50%;
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.02em;
        text-shadow: 0 3px 15px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: rgba(255, 255, 255, 0.95);
        margin-top: 0.75rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, #ff6f00, #ff9800);
        backdrop-filter: blur(10px);
        padding: 0.6rem 1.4rem;
        border-radius: 50px;
        color: #1a1a1a;
        font-size: 0.9rem;
        font-weight: 700;
        margin-top: 1rem;
        border: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 4px 15px rgba(255, 111, 0, 0.3);
    }
    
    /* ===== CHAT MESSAGES ===== */
    .chat-container {
        background: linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
        min-height: 400px;
        max-height: 600px;
        overflow-y: auto;
        border: 3px solid #aed581;
    }
    
    .message-wrapper {
        display: flex;
        margin-bottom: 1.5rem;
        animation: slideUp 0.4s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .user-message-wrapper {
        justify-content: flex-end;
    }
    
    .bot-message-wrapper {
        justify-content: flex-start;
    }
    
    .message-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        flex-shrink: 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border: 3px solid rgba(255, 255, 255, 0.5);
    }
    
    .user-avatar {
        background: linear-gradient(135deg, #1e88e5, #1565c0);
        order: 2;
        margin-left: 0.75rem;
    }
    
    .bot-avatar {
        background: linear-gradient(135deg, #43a047, #2e7d32);
        order: 1;
        margin-right: 0.75rem;
    }
    
    .message-content {
        max-width: 65%;
        padding: 1.3rem 1.6rem;
        border-radius: 18px;
        line-height: 1.6;
        font-size: 0.95rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .user-message {
        background: linear-gradient(135deg, #29b6f6, #0288d1);
        color: #1a1a1a;
        border-bottom-right-radius: 4px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        font-weight: 500;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #fff9c4, #fff59d);
        color: #1a1a1a;
        border: 2px solid #fdd835;
        border-bottom-left-radius: 4px;
        font-weight: 500;
    }
    
    /* ===== QUICK ACTION CARDS ===== */
    .quick-actions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .action-card {
        background: linear-gradient(135deg, #81d4fa 0%, #4fc3f7 100%);
        border-radius: 18px;
        padding: 2rem;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 3px solid #29b6f6;
        box-shadow: 0 6px 20px rgba(41, 182, 246, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .action-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #ff6f00, #ffa726, #66bb6a);
        transform: scaleX(0);
        transition: transform 0.4s ease;
    }
    
    .action-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 40px rgba(41, 182, 246, 0.4);
        border-color: #0288d1;
    }
    
    .action-card:hover::before {
        transform: scaleX(1);
    }
    
    .action-card:nth-child(1) {
        background: linear-gradient(135deg, #a5d6a7 0%, #81c784 100%);
        border-color: #66bb6a;
    }
    
    .action-card:nth-child(2) {
        background: linear-gradient(135deg, #ffcc80 0%, #ffb74d 100%);
        border-color: #ffa726;
    }
    
    .action-card:nth-child(3) {
        background: linear-gradient(135deg, #80deea 0%, #4dd0e1 100%);
        border-color: #26c6da;
    }
    
    .action-icon {
        font-size: 3.2rem;
        margin-bottom: 1rem;
        display: block;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
    }
    
    .action-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
        text-shadow: 0 1px 2px rgba(255,255,255,0.5);
    }
    
    .action-description {
        font-size: 0.9rem;
        color: #263238;
        line-height: 1.6;
        font-weight: 500;
    }
    
    /* ===== SIDEBAR STYLING ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #b2ebf2 0%, #80deea 50%, #4dd0e1 100%);
        border-right: 3px solid #26c6da;
    }
    
    [data-testid="stSidebar"] .sidebar-content {
        padding: 1.5rem;
    }
    
    .sidebar-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #00796b, #00acc1);
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 121, 107, 0.3);
    }
    
    .sidebar-logo {
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
    }
    
    .sidebar-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #1a1a1a;
        margin: 0;
        text-shadow: 0 1px 2px rgba(255,255,255,0.3);
    }
    
    .sidebar-tagline {
        font-size: 0.85rem;
        color: #263238;
        margin-top: 0.25rem;
        font-weight: 600;
    }
    
    .feature-section {
        background: linear-gradient(135deg, #fff9c4, #fff59d);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 3px solid #fdd835;
    }
    
    .feature-section-title {
    font-size: 1.2rem;
    font-weight: 800;
    color: black;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

    
    .feature-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .feature-item {
        padding: 0.85rem 0;
        color: #263238;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        border-bottom: 2px solid rgba(0,0,0,0.1);
        font-weight: 600;
    }
    
    .feature-item:last-child {
        border-bottom: none;
    }
    
    .feature-icon {
        font-size: 1.3rem;
        flex-shrink: 0;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #ff6f00, #ff9800);
        color: #1a1a1a;
        border: 3px solid #f57c00;
        border-radius: 14px;
        padding: 0.9rem 1.6rem;
        font-weight: 800;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(255, 111, 0, 0.3);
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(255, 111, 0, 0.4);
        background: linear-gradient(135deg, #f57c00, #ff9800);
        border-color: #e65100;
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, #c5e1a5, #aed581);
        border: 3px dashed #7cb342;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(124, 179, 66, 0.2);
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #558b2f;
        background: linear-gradient(135deg, #aed581, #9ccc65);
        transform: scale(1.02);
    }
    
    [data-testid="stFileUploader"] label {
        color: #1a1a1a !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    
    /* ===== CHAT INPUT ===== */
    .stChatInput {
        border-radius: 18px;
        background: linear-gradient(135deg, #e1f5fe, #b3e5fc);
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.15);
        border: 3px solid #4fc3f7;
    }
    
    .stChatInput:focus-within {
        border-color: #0288d1;
        box-shadow: 0 6px 30px rgba(2, 136, 209, 0.3);
        transform: scale(1.01);
    }
    
    /* ===== STATS CARDS ===== */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #ffccbc, #ffab91);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(255, 138, 101, 0.3);
        border: 3px solid #ff8a65;
    }
    
    .stat-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #bf360c;
        margin-bottom: 0.25rem;
        text-shadow: 0 1px 2px rgba(255,255,255,0.5);
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #263238;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
    }
    
    /* ===== ALERTS ===== */
    .custom-alert {
        background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
        border-left: 5px solid #66bb6a;
        border-radius: 12px;
        padding: 1.2rem 1.6rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(102, 187, 106, 0.3);
        border: 2px solid #4caf50;
    }
    
    .custom-alert.info {
        background: linear-gradient(135deg, #bbdefb, #90caf9);
        border-left-color: #2196f3;
        border-color: #42a5f5;
    }
    
    .custom-alert.warning {
        background: linear-gradient(135deg, #ffe0b2, #ffcc80);
        border-left-color: #ff9800;
        border-color: #ffa726;
    }
    
    .custom-alert.success {
        background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
        border-left-color: #4caf50;
        border-color: #66bb6a;
    }
    
    /* ===== FOOTER ===== */
    .footer-container {
        background: linear-gradient(135deg, #80cbc4, #4db6ac);
        border-radius: 18px;
        padding: 2rem;
        margin-top: 3rem;
        box-shadow: 0 -6px 25px rgba(0, 150, 136, 0.3);
        border: 3px solid #26a69a;
    }
    
    .footer-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        text-align: center;
    }
    
    .footer-item {
        padding: 1rem;
    }
    
    .footer-title {
        font-size: 0.9rem;
        color: #263238;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .footer-value {
        font-size: 1.2rem;
        font-weight: 800;
        color: #1a1a1a;
        text-shadow: 0 1px 2px rgba(255,255,255,0.3);
    }
    
    /* ===== SPINNER ===== */
    .stSpinner > div {
        border-top-color: #ff6f00 !important;
        border-right-color: #00acc1 !important;
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: linear-gradient(135deg, #b2dfdb, #80cbc4);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #ff6f00, #ff9800);
        border-radius: 10px;
        border: 2px solid #80cbc4;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #f57c00, #ffa726);
    }
    
    /* ===== RESPONSIVE DESIGN ===== */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2rem;
        }
        
        .hero-subtitle {
            font-size: 1rem;
        }
        
        .message-content {
            max-width: 85%;
        }
        
        .quick-actions-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* ===== PULSE ANIMATION FOR LOADING ===== */
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.6;
        }
    }
    
    .loading-pulse {
        animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* ===== GLOW EFFECTS ===== */
    @keyframes glow {
        0%, 100% {
            box-shadow: 0 0 20px rgba(255, 111, 0, 0.5);
        }
        50% {
            box-shadow: 0 0 35px rgba(255, 111, 0, 0.8);
        }
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
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0


# =============================
# CONFIG
# =============================
API_BASE_URL = "https://medassist-xr-1.onrender.com"
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
            return {"response": f"⚠️ Server Error ({response.status_code}). Please try again later."}
    except requests.exceptions.ConnectionError:
        return {"response": "⚠️ Unable to connect to backend server. Please ensure the API is running."}
    except Exception as e:
        return {"response": f"⚠️ Connection error: {str(e)}"}


def analyze_report_with_groq(pdf_file):
    """Analyze uploaded medical report with Groq AI"""
    report_text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                report_text += text + "\n"

    if not report_text.strip():
        return "❌ Could not extract readable text from the PDF. Please ensure the file is not password-protected or corrupted."

    prompt = f"""
    You are a professional medical assistant AI with expertise in interpreting medical reports.
    
    Analyze the following medical report and provide:
    1. A clear summary of the key findings
    2. Identification of any abnormal values with normal ranges
    3. General health guidance and lifestyle recommendations
    4. Important: State clearly that this is informational only and not a medical diagnosis
    
    Report Content:
    {report_text[:3000]}
    
    Provide the analysis in a well-structured, easy-to-understand format.
    """

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful, professional medical report interpreter. Always remind users to consult healthcare professionals."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error analyzing report: {str(e)}"


# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-logo">🏥</div>
        <h1 class="sidebar-title">MedAssist XR</h1>
        <p class="sidebar-tagline">Your AI Health Companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Section
    st.markdown("""
    <div class="feature-section">
        <h3 class="feature-section-title" style="color: black;">⚡ Core Features</h3>
        <ul class="feature-list">
            <li class="feature-item">
                <span class="feature-icon">🩺</span>
                <span>Symptom Analysis</span>
            </li>
            <li class="feature-item">
                <span class="feature-icon">📊</span>
                <span>Report Interpretation</span>
            </li>
            <li class="feature-item">
                <span class="feature-icon">💊</span>
                <span>Health Insights</span>
            </li>
            <li class="feature-item">
                <span class="feature-icon">🔒</span>
                <span>Secure & Private</span>
            </li>
            <li class="feature-item">
                <span class="feature-icon">⚡</span>
                <span>24/7 Availability</span>
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Section
    st.markdown("""
    <div class="feature-section">
        <h3 class="feature-section-title" style="color: #000000;">📈 Session Stats</h3>
        <div style="text-align: center; padding: 1rem 0;">
            <div class="stat-value">{}</div>
            <div class="stat-label">Messages Exchanged</div>
        </div>
    </div>
    """.format(len(st.session_state.messages)), unsafe_allow_html=True)
    
    # Doctor Finder Info
    st.markdown("""
    <div class="feature-section">
        <h3 class="feature-section-title" style="color: #000000;">👨‍⚕️ Find a Doctor</h3>
        <div class="custom-alert info">
            <p style="margin: 0; font-size: 0.9rem; color: #1a1a1a; font-weight: 600;">
                <strong>Coming Soon!</strong><br>
                Doctor finder feature will be available in the next update.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # New Chat Button
    if st.button("🆕 Start New Conversation", use_container_width=True, key="new_chat"):
        st.session_state.messages = []
        st.session_state.conversation_context = []
        st.session_state.chat_count = 0
        st.rerun()


# =============================
# MAIN HEADER
# =============================
st.markdown("""
<div class="hero-header">
    <h1 class="hero-title">🏥 MedAssist XR</h1>
    <p class="hero-subtitle">AI-Powered Multimodal Health Assistant for Smarter Healthcare Decisions</p>
    <span class="hero-badge">🔒 • Powered by Advanced AI</span>
</div>
""", unsafe_allow_html=True)


# =============================
# WELCOME SECTION / QUICK ACTIONS
# =============================
if not st.session_state.messages:
    st.markdown("<h2 style='text-align: center; color: #1a1a1a; margin: 2rem 0 1rem 0; font-size: 2.2rem; font-weight: 800;'>🚀 How Can I Help You Today?</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #263238; margin-bottom: 2rem; font-size: 1.1rem; font-weight: 600;'>Select an option below or type your health query</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="action-card">
            <span class="action-icon">🤒</span>
            <h3 class="action-title">Symptom Check</h3>
            <p class="action-description">Describe your symptoms and get AI-powered preliminary analysis</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Check Symptoms", key="btn_symptoms", use_container_width=True):
            user_input = "I have some symptoms I'd like to discuss. Can you help me understand what might be causing them?"
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.chat_count += 1
            with st.spinner("🤔 Analyzing..."):
                response = send_message(user_input)
                time.sleep(0.3)
                st.session_state.messages.append({"role": "assistant", "content": response["response"]})
                st.session_state.conversation_context.append({
                    "user": user_input,
                    "assistant": response["response"],
                    "timestamp": datetime.now().isoformat()
                })
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="action-card">
            <span class="action-icon">📊</span>
            <h3 class="action-title">Report Analysis</h3>
            <p class="action-description">Upload medical reports for detailed interpretation and insights</p>
        </div>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("📄 Upload PDF Report", type=["pdf"], key="report_uploader")
        if uploaded_file:
            with st.spinner("🔍 Analyzing your medical report..."):
                result = analyze_report_with_groq(uploaded_file)
                time.sleep(0.3)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"**📊 Medical Report Analysis**\n\n{result}"
            })
            st.session_state.chat_count += 1
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="action-card">
            <span class="action-icon">💡</span>
            <h3 class="action-title">Health Guidance</h3>
            <p class="action-description">Get personalized health tips and wellness recommendations</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Health Tips", key="btn_tips", use_container_width=True):
            user_input = "Can you provide me with some general health and wellness advice?"
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.chat_count += 1
            with st.spinner("💭 Preparing recommendations..."):
                response = send_message(user_input)
                time.sleep(0.3)
                st.session_state.messages.append({"role": "assistant", "content": response["response"]})
                st.session_state.conversation_context.append({
                    "user": user_input,
                    "assistant": response["response"],
                    "timestamp": datetime.now().isoformat()
                })
            st.rerun()


# =============================
# CHAT DISPLAY
# =============================
if st.session_state.messages:
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="message-wrapper user-message-wrapper">
                <div class="message-content user-message">
                    {msg['content']}
                </div>
                <div class="message-avatar user-avatar">👤</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message-wrapper bot-message-wrapper">
                <div class="message-avatar bot-avatar">🤖</div>
                <div class="message-content bot-message">
                    {msg['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


# =============================
# CHAT INPUT
# =============================
st.markdown("<br>", unsafe_allow_html=True)
user_input = st.chat_input("💬 Type your health query, paste lab results, or ask about symptoms...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.chat_count += 1
    
    with st.spinner("🤔 Processing your query..."):
        response = send_message(user_input)
        time.sleep(0.4)
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
st.markdown("""
<div class="footer-container">
    <div class="footer-grid">
        <div class="footer-item">
            <div class="footer-title">Version</div>
            <div class="footer-value">🏥 MedAssist XR v2.0</div>
        </div>
        <div class="footer-item">
            <div class="footer-title">Powered By</div>
            <div class="footer-value">⚡ GROQ AI + Streamlit</div>
        </div>
        <div class="footer-item">
            <div class="footer-title">Security</div>
            <div class="footer-value">🔒 End-to-End Encrypted</div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 3px solid #26a69a;">
        <p style="color: #1a1a1a; font-size: 0.9rem; margin: 0; font-weight: 600;">
            <strong>⚠️ Medical Disclaimer:</strong> MedAssist XR provides informational content only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for medical decisions.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
