# 🩺 MedAssist XR – Your AI-Powered Healthcare Companion  

---

> **Empowering healthcare through AI and intelligent diagnostics** 💊  
> Ask. Analyze. Act — with instant health insights and doctor discovery powered by LLMs & real APIs.  

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend%20API-teal?style=for-the-badge&logo=fastapi)
![Groq](https://img.shields.io/badge/Groq-LLM%20Powered-green?style=for-the-badge&logo=groq)
![Healthcare](https://img.shields.io/badge/Healthcare-AI%20Assistant-red?style=for-the-badge&logo=googlehealth)

---

## 📌 Overview  
**MedAssist XR** is an **AI-driven virtual healthcare assistant** that helps users analyze symptoms, interpret lab reports, find nearby doctors or hospitals, and get health insights — all through a **chat-based interface**.  

Built using **FastAPI**, **Groq LLM**, and real-world data sources like **Geoapify** and **Foursquare**, it bridges the gap between AI and accessible healthcare guidance.  

---

## 🚀 Live Demo  
Coming Soon... 🧠  
(Will be hosted on **Streamlit Cloud** and **Render** for backend deployment.)

---

## ✨ Features  
✅ AI-based symptom and health query analysis  
✅ Real-time doctor & hospital finder (via Geoapify + Foursquare APIs)  
✅ Smart chat interface powered by **Groq LLM (Llama-3.1-70B)**  
✅ Multi-service sidebar for easy access  
✅ FastAPI backend with clean RESTful endpoints  
✅ Secure API key management via `.env`  

---

## 🧠 How It Works  
1. User enters a query — e.g. *“Find a cardiologist near Mumbai”* or *“Explain my CBC report”*.  
2. The **FastAPI backend** routes the message to the **Groq-powered LLM**.  
3. If the query relates to doctors or hospitals, the system fetches verified results via **Foursquare** and **Geoapify APIs**.  
4. The response is returned as a structured, natural-language message ready for display in the chat interface.  

---

## 🛠 Tech Stack  

| Layer | Technology | Description |
|-------|-------------|-------------|
| **Frontend** | Streamlit | Clean and simple chat-based UI |
| **Backend** | FastAPI | Handles chat logic and API orchestration |
| **LLM** | Groq (Llama 3.1–70B) | Medical reasoning and health-related conversation |
| **APIs** | Foursquare, Geoapify | Real doctor & hospital data |
| **Styling** | Custom Streamlit CSS | Sidebar with health services menu |
| **Environment** | Python 3.8+, Uvicorn | For local and production deployment |

---

## ⚙️ Installation & Setup  

### 1️⃣ Clone Repository  
```bash
git clone https://github.com/anshkedia04/MedAssistXR.git
cd MedAssistXR/backend
