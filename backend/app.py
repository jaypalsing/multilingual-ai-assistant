from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.nlu import predict_intent
from backend.service_search import (
    detect_category,
    get_services_by_category,
    get_service_by_name,
    format_service_list,
    format_service_details,
)

app = FastAPI(title="ML BB ChatBot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Conversation memory
conversation_memory = {
    "last_services": []
}


class ChatRequest(BaseModel):
    message: str


def detect_language(text: str) -> str:
    text = text.strip()

    if not text:
        return "Unknown"

    if any(ch.isalpha() and ch.isascii() for ch in text):
        return "English"

    marathi_words = [
        "नमस्कार", "काय", "तुम्ही", "मला", "मदत", "हॅलो", "मी",
        "शाळा", "बँक", "रुग्णालय", "हॉटेल", "पोलीस", "फार्मसी"
    ]
    hindi_words = [
        "नमस्ते", "क्या", "आप", "मुझे", "मदद", "हेलो", "मैं",
        "अस्पताल", "स्कूल", "बैंक", "होटल", "पुलिस", "फार्मेसी"
    ]

    marathi_score = sum(1 for word in marathi_words if word in text)
    hindi_score = sum(1 for word in hindi_words if word in text)

    if marathi_score > hindi_score and marathi_score > 0:
        return "Marathi"

    if hindi_score > marathi_score and hindi_score > 0:
        return "Hindi"

    if any("\u0900" <= ch <= "\u097F" for ch in text):
        return "Hindi/Marathi"

    return "Unknown"


def detect_number_reference(text: str):
    text = text.lower().strip()

    if "first" in text or "1" in text or "पहिला" in text or "पहले" in text:
        return 0
    if "second" in text or "2" in text or "दुसरा" in text or "दूसरा" in text:
        return 1
    if "third" in text or "3" in text or "तिसरा" in text or "तीसरा" in text:
        return 2

    return None


def generate_reply(language: str, intent: str) -> str:
    replies = {
        "greeting": {
            "English": "Hello! Welcome to ML BB ChatBot.",
            "Hindi": "नमस्ते! ML BB ChatBot में आपका स्वागत है।",
            "Marathi": "नमस्कार! ML BB ChatBot मध्ये तुमचे स्वागत आहे.",
            "Hindi/Marathi": "नमस्ते / नमस्कार! ML BB ChatBot मध्ये आपले स्वागत आहे."
        },
        "thanks": {
            "English": "Thank you! I am here to help you.",
            "Hindi": "धन्यवाद! मैं आपकी मदद के लिए यहाँ हूँ।",
            "Marathi": "धन्यवाद! मी तुमच्या मदतीसाठी येथे आहे.",
            "Hindi/Marathi": "धन्यवाद! मी / मैं आपकी मदद के लिए यहाँ हूँ।"
        },
        "goodbye": {
            "English": "Goodbye! See you again.",
            "Hindi": "धन्यवाद! फिर मिलते हैं।",
            "Marathi": "धन्यवाद! पुन्हा भेटूया.",
            "Hindi/Marathi": "धन्यवाद! फिर मिलते हैं / पुन्हा भेटूया."
        },
        "help": {
            "English": "Yes, I can help you. Please tell me your query.",
            "Hindi": "हाँ, मैं आपकी मदद कर सकता हूँ। कृपया अपना प्रश्न बताइए।",
            "Marathi": "हो, मी तुमची मदत करू शकतो. कृपया तुमचा प्रश्न सांगा.",
            "Hindi/Marathi": "हो / हाँ, कृपया तुमचा / अपना प्रश्न सांगा।"
        },
        "chatbot_info": {
            "English": "I am a multilingual AI chatbot.",
            "Hindi": "मैं एक बहुभाषिक AI चैटबॉट हूँ।",
            "Marathi": "मी एक बहुभाषिक AI चॅटबॉट आहे.",
            "Hindi/Marathi": "मी / मैं एक बहुभाषिक AI chatbot आहे / हूँ।"
        },
        "personal_assistant": {
            "English": "I can work as your text-based personal assistant.",
            "Hindi": "मैं आपके टेक्स्ट-आधारित पर्सनल असिस्टेंट के रूप में काम कर सकता हूँ।",
            "Marathi": "मी तुमचा टेक्स्ट-आधारित वैयक्तिक सहाय्यक म्हणून काम करू शकतो.",
            "Hindi/Marathi": "मी / मैं तुमचा / आपका text-based personal assistant आहे / हूँ।"
        },
        "search_service": {
            "English": "Please tell me which service you need, like hospital, school, bank, police station, hotel, or pharmacy.",
            "Hindi": "कृपया बताइए आपको कौन सी सेवा चाहिए, जैसे अस्पताल, स्कूल, बैंक, पुलिस स्टेशन, होटल या फार्मेसी।",
            "Marathi": "कृपया सांगा तुम्हाला कोणती सेवा हवी आहे, जसे हॉस्पिटल, शाळा, बँक, पोलीस स्टेशन, हॉटेल किंवा फार्मसी.",
            "Hindi/Marathi": "कृपया सांगा / बताइए तुम्हाला / आपको कोणती / कौन सी सेवा हवी आहे / चाहिए।"
        },
        "service_details": {
            "English": "Please tell me the name of the place whose details you want.",
            "Hindi": "कृपया उस स्थान का नाम बताइए जिसकी जानकारी चाहिए।",
            "Marathi": "कृपया ज्या ठिकाणाची माहिती हवी आहे त्याचे नाव सांगा.",
            "Hindi/Marathi": "कृपया नाव / नाम सांगा / बताइए."
        },
    }

    if intent in replies:
        return replies[intent].get(language, replies[intent]["English"])

    return "I understood your message. More advanced response generation will be added next."


@app.get("/")
def home():
    return {"message": "ML BB ChatBot API is running"}


@app.post("/chat")
def chat(request: ChatRequest):
    message = request.message.strip()

    try:
        language = detect_language(message)

        # 1. Direct service name match
        matched_service = get_service_by_name(message)
        if matched_service:
            return {
                "message": message,
                "language": language,
                "intent": "service_details",
                "confidence": 0.95,
                "reply": format_service_details(matched_service)
            }

        # 2. Conversation memory: first / second / third one
        ref_index = detect_number_reference(message)
        if ref_index is not None:
            last_services = conversation_memory.get("last_services", [])

            if last_services and ref_index < len(last_services):
                selected_service = last_services[ref_index]
                return {
                    "message": message,
                    "language": language,
                    "intent": "service_details",
                    "confidence": 0.96,
                    "reply": format_service_details(selected_service)
                }

        # 3. Category-based service search
        matched_category = detect_category(message)
        if matched_category:
            services = get_services_by_category(matched_category)

            # Store service list in memory
            conversation_memory["last_services"] = services

            return {
                "message": message,
                "language": language,
                "intent": "search_service",
                "confidence": 0.93,
                "reply": format_service_list(matched_category, services)
            }

        # 4. ML model fallback
        intent, confidence = predict_intent(message)
        reply = generate_reply(language, intent)

        # Lower confidence threshold to avoid rejecting simple greetings
        if confidence < 0.25:
            return {
                "message": message,
                "language": language,
                "intent": "unknown",
                "confidence": round(confidence, 2),
                "reply": (
                    "Sorry, I could not clearly understand your request. "
                    "You can ask about hospital, school, bank, police station, hotel, pharmacy, "
                    "or general chatbot help."
                )
            }

        return {
            "message": message,
            "language": language,
            "intent": intent,
            "confidence": round(confidence, 2),
            "reply": reply
        }

    except Exception as e:
        return {
            "message": message,
            "language": "Error",
            "intent": "Error",
            "confidence": 0.0,
            "reply": f"Backend error: {str(e)}"
        }