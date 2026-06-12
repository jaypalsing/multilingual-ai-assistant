from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.nlu import predict_intent

 
from backend.service_search import (

    CATEGORY_KEYWORDS,
    detect_category,
    get_services_by_category,
    get_service_by_name,
    format_service_list,
    format_service_details
)
 


# =========================================================
# FASTAPI INITIALIZATION
# =========================================================

app = FastAPI(
    title="MultiLinguaAI API",
    version="1.0.0",
    description="""
    AI-Powered Multilingual Conversational Assistant
    using NLP, Machine Learning, and FastAPI.
    """
)

# =========================================================
# CORS CONFIGURATION
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# CONVERSATION MEMORY
# =========================================================

conversation_memory = {
    "last_services": []
}

# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):
    message: str

# =========================================================
# LANGUAGE DETECTION
# =========================================================

def detect_language(text: str) -> str:

    text = text.strip()

    if not text:
        return "Unknown"

    # =====================================================
    # ENGLISH DETECTION
    # =====================================================

    if any(ch.isalpha() and ch.isascii() for ch in text):
        return "English"

    # =====================================================
    # MARATHI WORDS
    # =====================================================

    marathi_words = [
        "नमस्कार", "काय", "तुम्ही", "मला",
        "मदत", "हॅलो", "मी", "शाळा",
        "बँक", "रुग्णालय", "हॉटेल",
        "पोलीस", "फार्मसी"
    ]

    # =====================================================
    # HINDI WORDS
    # =====================================================

    hindi_words = [
        "नमस्ते", "क्या", "आप", "मुझे",
        "मदद", "हेलो", "मैं", "अस्पताल",
        "स्कूल", "बैंक", "होटल",
        "पुलिस", "फार्मेसी"
    ]

    marathi_score = sum(
        1 for word in marathi_words if word in text
    )

    hindi_score = sum(
        1 for word in hindi_words if word in text
    )

    if marathi_score > hindi_score and marathi_score > 0:
        return "Marathi"

    if hindi_score > marathi_score and hindi_score > 0:
        return "Hindi"

    if any("\u0900" <= ch <= "\u097F" for ch in text):
        return "Hindi/Marathi"

    return "Unknown"

# =========================================================
# NUMBER REFERENCE DETECTION
# =========================================================

def detect_number_reference(text: str):

    text = text.lower().strip()

    if (
        "first" in text or
        "1" in text or
        "पहिला" in text or
        "पहले" in text
    ):
        return 0

    if (
        "second" in text or
        "2" in text or
        "दुसरा" in text or
        "दूसरा" in text
    ):
        return 1

    if (
        "third" in text or
        "3" in text or
        "तिसरा" in text or
        "तीसरा" in text
    ):
        return 2

    return None

# =========================================================
# RESPONSE GENERATION
# =========================================================

def generate_reply(language: str, intent: str) -> str:

    replies = {

        # =================================================
        # GREETING
        # =================================================

        "greeting": {

            "English":
                "Hello! Welcome to MultiLinguaAI.",

            "Hindi":
                "नमस्ते! MultiLinguaAI में आपका स्वागत है।",

            "Marathi":
                "नमस्कार! MultiLinguaAI मध्ये तुमचे स्वागत आहे.",

            "Hindi/Marathi":
                "नमस्ते / नमस्कार! MultiLinguaAI मध्ये आपले स्वागत आहे।"
        },

        # =================================================
        # THANKS
        # =================================================

        "thanks": {

            "English":
                "Thank you! I am here to help you.",

            "Hindi":
                "धन्यवाद! मैं आपकी मदद के लिए यहाँ हूँ।",

            "Marathi":
                "धन्यवाद! मी तुमच्या मदतीसाठी येथे आहे.",

            "Hindi/Marathi":
                "धन्यवाद! मी / मैं आपकी मदद के लिए यहाँ हूँ।"
        },

        # =================================================
        # GOODBYE
        # =================================================

        "goodbye": {

            "English":
                "Goodbye! See you again.",

            "Hindi":
                "धन्यवाद! फिर मिलते हैं।",

            "Marathi":
                "धन्यवाद! पुन्हा भेटूया.",

            "Hindi/Marathi":
                "धन्यवाद! फिर मिलते हैं / पुन्हा भेटूया।"
        },

        # =================================================
        # HELP
        # =================================================

        "help": {

            "English":
                "Yes, I can help you. Please tell me your query.",

            "Hindi":
                "हाँ, मैं आपकी मदद कर सकता हूँ। कृपया अपना प्रश्न बताइए।",

            "Marathi":
                "हो, मी तुमची मदत करू शकतो. कृपया तुमचा प्रश्न सांगा.",

            "Hindi/Marathi":
                "हो / हाँ, कृपया तुमचा / अपना प्रश्न सांगा।"
        },

        # =================================================
        # CHATBOT INFO
        # =================================================

        "chatbot_info": {

            "English":
                "I am MultiLinguaAI, a multilingual AI-powered virtual assistant.",

            "Hindi":
                "मैं MultiLinguaAI हूँ, एक बहुभाषिक AI वर्चुअल असिस्टेंट।",

            "Marathi":
                "मी MultiLinguaAI आहे, एक बहुभाषिक AI व्हर्च्युअल सहाय्यक.",

            "Hindi/Marathi":
                "मी / मैं MultiLinguaAI आहे / हूँ।"
        },

        # =================================================
        # PERSONAL ASSISTANT
        # =================================================

        "personal_assistant": {

            "English":
                "I can work as your AI-powered personal assistant.",

            "Hindi":
                "मैं आपके AI आधारित पर्सनल असिस्टेंट के रूप में काम कर सकता हूँ।",

            "Marathi":
                "मी तुमचा AI आधारित वैयक्तिक सहाय्यक म्हणून काम करू शकतो.",

            "Hindi/Marathi":
                "मी / मैं तुमचा / आपका AI personal assistant आहे / हूँ।"
        },

        # =================================================
        # SEARCH SERVICE
        # =================================================

        "search_service": {

            "English":
                "Please tell me which service you need like hospital, school, bank, hotel, pharmacy, or police station.",

            "Hindi":
                "कृपया बताइए आपको कौन सी सेवा चाहिए जैसे अस्पताल, स्कूल, बैंक, होटल, फार्मेसी या पुलिस स्टेशन।",

            "Marathi":
                "कृपया सांगा तुम्हाला कोणती सेवा हवी आहे जसे हॉस्पिटल, शाळा, बँक, हॉटेल, फार्मसी किंवा पोलीस स्टेशन.",

            "Hindi/Marathi":
                "कृपया सांगा / बताइए तुम्हाला / आपको कोणती / कौन सी सेवा हवी आहे / चाहिए।"
        },

        # =================================================
        # SERVICE DETAILS
        # =================================================

        "service_details": {

            "English":
                "Please tell me the service name whose details you need.",

            "Hindi":
                "कृपया उस सेवा का नाम बताइए जिसकी जानकारी चाहिए।",

            "Marathi":
                "कृपया ज्या सेवेची माहिती हवी आहे त्याचे नाव सांगा.",

            "Hindi/Marathi":
                "कृपया नाव / नाम सांगा / बताइए।"
        },


        "how_are_you": {

            "English":
                "I am doing great! How can I help you today?",

            "Hindi":
                "मैं बिल्कुल ठीक हूँ। मैं आपकी कैसे मदद कर सकता हूँ?",

            "Marathi":
                "मी छान आहे. मी तुम्हाला कशी मदत करू शकतो?",

            "Hindi/Marathi":
                "मी / मैं ठीक आहे / हूँ।"
        }



    }

    if intent in replies:
        return replies[intent].get(
            language,
            replies[intent]["English"]
        )

    return (
        "I understood your message. "
        "Advanced AI response generation "
        "will be added soon."
    )

# =========================================================
# ROOT API
# =========================================================

@app.get("/", tags=["System"])

def home():

    return {
        "message": "MultiLinguaAI API is running successfully",
        "status": "active",
        "version": "1.0.0"
    }

# =========================================================
# HEALTH CHECK API
# =========================================================

@app.get("/health", tags=["System"])

def health_check():

    return {
        "status": "healthy",
        "application": "MultiLinguaAI",
        "version": "1.0.0"
    }



 
# =========================================================
# CHAT API
# =========================================================

@app.post("/chat", tags=["Chat"])

def chat(request: ChatRequest):

    message = request.message.strip()

    try:

        # =================================================
        # NLP PREDICTION
        # =================================================

        prediction = predict_intent(message)

        intent = prediction["intent"]

        confidence = prediction["confidence"]

        language_code = prediction["language"]

        # =================================================
        # LANGUAGE FORMAT
        # =================================================

        if language_code == "hi":

            language = "Hindi"

        elif language_code == "mr":

            language = "Marathi"

        else:

            language = "English"

        lang_code = (
            "mr" if language == "Marathi"
            else "hi" if language == "Hindi"
            else "en"
        )

        # =================================================
        # COMMON COMMUNICATION
        # =================================================

        if intent in [

            "greeting",
            "how_are_you",
            "thanks",
            "goodbye",
            "help",
            "chatbot_info",
            "personal_assistant"

        ]:

            return {

                "message": message,
                "language": language,
                "intent": intent,
                "confidence": round(confidence, 2),

                "reply": generate_reply(
                    language,
                    intent
                )
            }

        # =================================================
        # MEMORY REFERENCE
        # =================================================

        ref_index = detect_number_reference(message)

        if ref_index is not None:

            last_services = conversation_memory.get(
                "last_services",
                []
            )

            if (
                last_services and
                ref_index < len(last_services)
            ):

                selected_service = last_services[ref_index]

                return {

                    "message": message,
                    "language": language,
                    "intent": "service_details",
                    "confidence": 0.96,

                    "reply": format_service_details(
                        selected_service,
                        lang_code
                    )
                }

 
        # =================================================
        # CATEGORY SEARCH
        # =================================================

        matched_category = detect_category(message)

        if matched_category:

            # =============================================
            # DETECT TOP NUMBER
            # =============================================

            limit = 10

            import re

            number_match = re.search(r"\d+", message)

            if number_match:

                limit = int(number_match.group())

                # Safety limit
                limit = min(limit, 20)

            services = get_services_by_category(

                matched_category,

                limit=limit
            )

            conversation_memory["last_services"] = services

            return {

                "message": message,

                "language": language,

                "intent": "search_service",

                "confidence": 0.93,

                "reply": format_service_list(

                    matched_category,

                    services,

                    lang_code
                )
            }
        

        # =================================================
        # DIRECT SERVICE SEARCH
        # =================================================

        matched_service = get_service_by_name(message)

        if matched_service:

            return {

                "message": message,
                "language": language,
                "intent": "service_details",
                "confidence": 0.95,

                "reply": format_service_details(

                    matched_service,
                    lang_code
                )
            }

        # =================================================
        # LOW CONFIDENCE
        # =================================================

        if confidence < 0.25:

            unknown_reply = {

                "English":
                    "Sorry, I could not understand your request clearly. Please ask about hospitals, schools, colleges, hotels, pharmacies, or services.",

                "Hindi":
                    "माफ़ कीजिए, मैं आपका प्रश्न समझ नहीं पाया। कृपया अस्पताल, स्कूल, कॉलेज, होटल या सेवाओं के बारे में पूछें।",

                "Marathi":
                    "माफ करा, मला तुमचा प्रश्न समजला नाही. कृपया हॉस्पिटल, शाळा, कॉलेज, हॉटेल किंवा सेवांबद्दल विचारा."
            }

            return {

                "message": message,
                "language": language,
                "intent": "unknown",
                "confidence": round(confidence, 2),

                "reply": unknown_reply.get(
                    language,
                    unknown_reply["English"]
                )
            }

        # =================================================
        # DEFAULT FALLBACK
        # =================================================

        return {

            "message": message,
            "language": language,
            "intent": intent,
            "confidence": round(confidence, 2),

            "reply":
                "I understood your request. More intelligent response generation will be added soon."
        }

    except Exception as e:

        return {

            "message": message,
            "language": "Error",
            "intent": "Error",
            "confidence": 0.0,

            "reply": f"Backend error: {str(e)}"
        }
 