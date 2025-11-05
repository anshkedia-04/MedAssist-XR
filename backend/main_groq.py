# """
# MedAssist XR – Groq LLM + Foursquare + Geoapify + Weather
# """

# from fastapi import FastAPI, HTTPException, Query
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Optional, List
# import os
# from datetime import datetime
# import requests
# from dotenv import load_dotenv
# from fastapi.responses import JSONResponse
# from groq import Groq

# # ========================================
# # ENV SETUP
# # ========================================
# load_dotenv()

# app = FastAPI(title="MedAssist XR API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ========================================
# # API KEYS
# # ========================================
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")
# GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
# OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# # ========================================
# # GROQ INITIALIZATION
# # ========================================
# USE_GROQ = GROQ_API_KEY is not None
# if USE_GROQ:
#     try:
#         groq_client = Groq(api_key=GROQ_API_KEY)
#         print("✅ Groq LLM enabled")
#     except Exception as e:
#         print(f"⚠️ Groq error: {e}")
#         USE_GROQ = False
# else:
#     print("ℹ️ Running without LLM (fallback mode)")


# # ========================================
# # MODELS
# # ========================================
# class ChatRequest(BaseModel):
#     message: str
#     context: Optional[List[dict]] = []
#     use_llm: Optional[bool] = True


# class ChatResponse(BaseModel):
#     response: str
#     suggestions: Optional[List[str]] = []
#     category: str
#     llm_used: bool = False


# # ========================================
# # BASIC MEDICAL DATA
# # ========================================
# MEDICAL_KNOWLEDGE = {
#     "symptoms": {
#         "fever": {"description": "Elevated body temperature.", "possible_causes": ["Viral infection", "Bacterial infection"], "recommendations": ["Rest", "Hydrate", "Monitor temperature"]},
#         "cough": {"description": "Reflex to clear airways.", "possible_causes": ["Cold", "Allergy"], "recommendations": ["Stay hydrated", "Avoid smoke", "Use humidifier"]},
#         "headache": {"description": "Pain in head or upper neck region.", "possible_causes": ["Stress", "Migraine"], "recommendations": ["Rest", "Avoid bright light"]},
#         "chest pain": {"description": "Discomfort in the chest area.", "possible_causes": ["Heart issue", "Muscle strain"], "recommendations": ["Seek immediate help if severe"]}
#     }
# }


# # ========================================
# # API HELPERS
# # ========================================

# def find_nearby_doctors(location: str) -> list:
#     """
#     Try Foursquare first, then Geoapify.
#     """
#     # ---- Try Foursquare ----
#     if FOURSQUARE_API_KEY:
#         try:
#             url = "https://api.foursquare.com/v3/places/search"
#             headers = {"Accept": "application/json", "Authorization": FOURSQUARE_API_KEY}
#             params = {"query": "doctor", "near": location, "limit": 5}
#             r = requests.get(url, headers=headers, params=params)
#             r.raise_for_status()
#             results = r.json().get("results", [])
#             if results:
#                 return [{"name": res.get("name", "Unknown"),
#                          "address": res.get("location", {}).get("formatted_address", "No address")} for res in results]
#         except Exception as e:
#             print(f"⚠️ Foursquare error: {e}")

#     # ---- Fallback to Geoapify ----
#     if GEOAPIFY_API_KEY:
#         try:
#             url = (
#                 f"https://api.geoapify.com/v2/places"
#                 f"?categories=healthcare.hospital,healthcare.clinic,healthcare.doctor"
#                 f"&text={location}&limit=5&apiKey={GEOAPIFY_API_KEY}"
#             )
#             r = requests.get(url)
#             r.raise_for_status()
#             data = r.json()
#             features = data.get("features", [])
#             if features:
#                 return [
#                     {
#                         "name": f["properties"].get("name", "Unknown"),
#                         "address": f["properties"].get("formatted", "No address found")
#                     }
#                     for f in features
#                 ]
#         except Exception as e:
#             print(f"⚠️ Geoapify error: {e}")

#     return []


# def get_weather(location: str) -> str:
#     """Fetch weather details from OpenWeatherMap"""
#     try:
#         url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
#         res = requests.get(url).json()
#         if res.get("main"):
#             return f"🌤️ {location}: {res['main']['temp']}°C, {res['weather'][0]['description'].capitalize()}."
#         return "Weather unavailable."
#     except Exception as e:
#         print("Weather error:", e)
#         return "Unable to fetch weather."


# # ========================================
# # LLM / FALLBACK SYSTEM
# # ========================================

# def categorize_query(q: str) -> str:
#     q = q.lower()
#     if "doctor" in q:
#         return "doctor_search"
#     if "weather" in q:
#         return "weather"
#     if any(s in q for s in MEDICAL_KNOWLEDGE["symptoms"]):
#         return "symptom_inquiry"
#     return "general"


# def generate_suggestions(cat: str) -> List[str]:
#     suggestions = {
#         "doctor_search": ["Find hospitals", "Find doctors nearby"],
#         "weather": ["Check another city", "See humidity"],
#         "symptom_inquiry": ["Find doctor", "Get remedies"],
#         "general": ["Find doctor", "Ask about symptoms", "Check weather"]
#     }
#     return suggestions.get(cat, ["Ask another question"])


# def fallback_response(message: str) -> ChatResponse:
#     cat = categorize_query(message)

#     if cat == "doctor_search":
#         doctors = find_nearby_doctors("Mumbai")
#         if doctors:
#             info = "\n".join([f"👨‍⚕️ {d['name']} — {d['address']}" for d in doctors])
#             return ChatResponse(response=f"Here are some doctors:\n\n{info}", suggestions=generate_suggestions(cat), category=cat)

#         return ChatResponse(response="No doctors found nearby.", suggestions=generate_suggestions(cat), category=cat)

#     if cat == "weather":
#         return ChatResponse(response=get_weather("Mumbai"), suggestions=generate_suggestions(cat), category=cat)

#     for s, info in MEDICAL_KNOWLEDGE["symptoms"].items():
#         if s in message.lower():
#             text = (
#                 f"**{s.title()}**\n"
#                 f"📝 {info['description']}\n"
#                 f"🔍 Causes: {', '.join(info['possible_causes'])}\n"
#                 f"💡 Tips:\n" + "\n".join([f"• {r}" for r in info['recommendations']])
#             )
#             return ChatResponse(response=text, suggestions=generate_suggestions(cat), category=cat)

#     return ChatResponse(response="Hi! I'm MedAssist XR. You can ask about symptoms, doctors, or weather.", suggestions=generate_suggestions(cat), category="general")


# def create_prompt(query: str, context: List[dict] = None) -> str:
#     system = "You are MedAssist XR, a friendly AI healthcare assistant."
#     history = ""
#     if context:
#         for msg in context[-3:]:
#             history += f"\nUser: {msg.get('user', '')}\nAssistant: {msg.get('assistant', '')}"
#     return f"{system}\n{history}\nUser: {query}\nAnswer clearly."


# def generate_llm_response(query: str, context: List[dict] = None) -> dict:
#     if not USE_GROQ:
#         return None
#     try:
#         prompt = create_prompt(query, context)
#         response = groq_client.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.3,
#             max_tokens=800
#         )
#         text = response.choices[0].message.content
#         cat = categorize_query(query)
#         return {"response": text, "suggestions": generate_suggestions(cat), "category": cat, "llm_used": True}
#     except Exception as e:
#         print(f"Groq error: {e}")
#         return None


# # ========================================
# # ROUTES
# # ========================================

# @app.post("/chat", response_model=ChatResponse)
# async def chat(req: ChatRequest):
#     if USE_GROQ and req.use_llm:
#         llm = generate_llm_response(req.message, req.context)
#         if llm:
#             return ChatResponse(**llm)
#     return fallback_response(req.message)


# @app.get("/find_doctor")
# def find_doctor_endpoint(location: str = Query(...)):
#     doctors = find_nearby_doctors(location)
#     if not doctors:
#         raise HTTPException(status_code=404, detail="No doctors found for this location.")
#     return {"location": location, "results": doctors}


# @app.get("/")
# def root():
#     return {"message": "✅ MedAssist XR API running", "LLM": USE_GROQ}


# @app.get("/health")
# def health():
#     return {"status": "ok", "time": datetime.now().isoformat()}


# # ========================================
# # RUN LOCALLY
# # ========================================
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)



"""
MedAssist XR – Groq LLM + Foursquare + Geoapify + Weather
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime
import requests
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from groq import Groq

# ========================================
# ENV SETUP
# ========================================
load_dotenv()

app = FastAPI(title="MedAssist XR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# API KEYS
# ========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# ========================================
# GROQ INITIALIZATION
# ========================================
USE_GROQ = GROQ_API_KEY is not None
if USE_GROQ:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq LLM enabled")
    except Exception as e:
        print(f"⚠️ Groq error: {e}")
        USE_GROQ = False
else:
    print("ℹ️ Running without LLM (fallback mode)")


# ========================================
# MODELS
# ========================================
class ChatRequest(BaseModel):
    message: str
    context: Optional[List[dict]] = []
    use_llm: Optional[bool] = True


class ChatResponse(BaseModel):
    response: str
    suggestions: Optional[List[str]] = []
    category: str
    llm_used: bool = False


# ========================================
# BASIC MEDICAL DATA
# ========================================
MEDICAL_KNOWLEDGE = {
    "symptoms": {
        "fever": {"description": "Elevated body temperature.", "possible_causes": ["Viral infection", "Bacterial infection"], "recommendations": ["Rest", "Hydrate", "Monitor temperature"]},
        "cough": {"description": "Reflex to clear airways.", "possible_causes": ["Cold", "Allergy"], "recommendations": ["Stay hydrated", "Avoid smoke", "Use humidifier"]},
        "headache": {"description": "Pain in head or upper neck region.", "possible_causes": ["Stress", "Migraine"], "recommendations": ["Rest", "Avoid bright light"]},
        "chest pain": {"description": "Discomfort in the chest area.", "possible_causes": ["Heart issue", "Muscle strain"], "recommendations": ["Seek immediate help if severe"]}
    }
}


# ========================================
# API HELPERS
# ========================================

def find_nearby_doctors(location: str) -> list:
    """
    Try Foursquare first, then Geoapify.
    """
    # ---- Try Foursquare ----
    if FOURSQUARE_API_KEY:
        try:
            url = "https://api.foursquare.com/v3/places/search"
            headers = {"Accept": "application/json", "Authorization": FOURSQUARE_API_KEY}
            params = {"query": "doctor", "near": location, "limit": 5}
            r = requests.get(url, headers=headers, params=params, timeout=8)
            r.raise_for_status()
            results = r.json().get("results", [])
            if results:
                return [{"name": res.get("name", "Unknown"),
                         "address": res.get("location", {}).get("formatted_address", "No address")} for res in results]
        except Exception as e:
            print(f"⚠️ Foursquare error: {e}")

    # ---- Fallback to Geoapify ----
    if GEOAPIFY_API_KEY:
        try:
            url = "https://api.geoapify.com/v2/places"
            params = {
                "categories": "healthcare.hospital,healthcare.clinic,healthcare.doctor",
                "text": location,
                "limit": 5,
                "apiKey": GEOAPIFY_API_KEY
            }
            r = requests.get(url, params=params, timeout=8)
            r.raise_for_status()
            data = r.json()
            features = data.get("features", [])
            if features:
                return [
                    {
                        "name": f["properties"].get("name", "Unknown"),
                        "address": f["properties"].get("formatted", "No address found")
                    }
                    for f in features
                ]
        except Exception as e:
            print(f"⚠️ Geoapify error: {e}")

    return []


def get_weather(location: str) -> str:
    """Fetch weather details from OpenWeatherMap"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {"q": location, "appid": OPENWEATHERMAP_API_KEY, "units": "metric"}
        res = requests.get(url, params=params, timeout=8).json()
        if res.get("main"):
            return f"🌤️ {location}: {res['main']['temp']}°C, {res['weather'][0]['description'].capitalize()}."
        return "Weather unavailable."
    except Exception as e:
        print("Weather error:", e)
        return "Unable to fetch weather."


# ========================================
# LLM / FALLBACK SYSTEM
# ========================================

def categorize_query(q: str) -> str:
    q = q.lower()
    if "doctor" in q:
        return "doctor_search"
    if "weather" in q:
        return "weather"
    if any(s in q for s in MEDICAL_KNOWLEDGE["symptoms"]):
        return "symptom_inquiry"
    return "general"


def generate_suggestions(cat: str) -> List[str]:
    suggestions = {
        "doctor_search": ["Find hospitals", "Find doctors nearby"],
        "weather": ["Check another city", "See humidity"],
        "symptom_inquiry": ["Find doctor", "Get remedies"],
        "general": ["Find doctor", "Ask about symptoms", "Check weather"]
    }
    return suggestions.get(cat, ["Ask another question"])


def fallback_response(message: str) -> ChatResponse:
    cat = categorize_query(message)

    if cat == "doctor_search":
        doctors = find_nearby_doctors("Mumbai")
        if doctors:
            info = "\n".join([f"👨‍⚕️ {d['name']} — {d['address']}" for d in doctors])
            return ChatResponse(response=f"Here are some doctors:\n\n{info}", suggestions=generate_suggestions(cat), category=cat)

        return ChatResponse(response="No doctors found nearby.", suggestions=generate_suggestions(cat), category=cat)

    if cat == "weather":
        return ChatResponse(response=get_weather("Mumbai"), suggestions=generate_suggestions(cat), category=cat)

    for s, info in MEDICAL_KNOWLEDGE["symptoms"].items():
        if s in message.lower():
            text = (
                f"**{s.title()}**\n"
                f"📝 {info['description']}\n"
                f"🔍 Causes: {', '.join(info['possible_causes'])}\n"
                f"💡 Tips:\n" + "\n".join([f"• {r}" for r in info['recommendations']])
            )
            return ChatResponse(response=text, suggestions=generate_suggestions(cat), category=cat)

    return ChatResponse(response="Hi! I'm MedAssist XR. You can ask about symptoms, doctors, or weather.", suggestions=generate_suggestions(cat), category="general")


def create_prompt(query: str, context: List[dict] = None) -> str:
    system = "You are MedAssist XR, a friendly AI healthcare assistant."
    history = ""
    if context:
        for msg in context[-3:]:
            history += f"\nUser: {msg.get('user', '')}\nAssistant: {msg.get('assistant', '')}"
    return f"{system}\n{history}\nUser: {query}\nAnswer clearly."


def generate_llm_response(query: str, context: List[dict] = None) -> dict:
    if not USE_GROQ:
        return None
    try:
        prompt = create_prompt(query, context)
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        text = response.choices[0].message.content
        cat = categorize_query(query)
        return {"response": text, "suggestions": generate_suggestions(cat), "category": cat, "llm_used": True}
    except Exception as e:
        print(f"Groq error: {e}")
        return None


# ========================================
# ROUTES
# ========================================

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if USE_GROQ and req.use_llm:
        llm = generate_llm_response(req.message, req.context)
        if llm:
            return ChatResponse(**llm)
    return fallback_response(req.message)


@app.get("/find_doctor")
def find_doctor_endpoint(location: str = Query(...)):
    doctors = find_nearby_doctors(location)
    if not doctors:
        raise HTTPException(status_code=404, detail="No doctors found for this location.")
    return {"location": location, "results": doctors}


@app.get("/")
def root():
    return {"message": "✅ MedAssist XR API running", "LLM": USE_GROQ}


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


# ========================================
# RUN LOCALLY
# ========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)