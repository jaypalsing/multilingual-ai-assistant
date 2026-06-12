import os
import pickle
import re
from langdetect import detect

# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_DIR = os.path.join(BASE_DIR, "models")

# =========================================================
# LOAD MODELS
# =========================================================

with open(os.path.join(MODEL_DIR, "intent_model.pkl"), "rb") as f:
    model = pickle.load(f)

with open(os.path.join(MODEL_DIR, "vectorizer.pkl"), "rb") as f:
    vectorizer = pickle.load(f)

with open(os.path.join(MODEL_DIR, "label_encoder.pkl"), "rb") as f:
    label_encoder = pickle.load(f)

# =========================================================
# MULTILINGUAL COMMON INTENTS
# =========================================================







COMMON_INTENTS = {

    # =====================================================
    # GREETING
    # =====================================================

    "greeting": [

        # English
        "hi",
        "hello",
        "hey",
        "good morning",
        "good evening",
        "good afternoon",

        # Hindi
        "नमस्ते",
        "हेलो",
        "हाय",
        "नमस्कार",

        # Marathi
        "नमस्कार",
        "हॅलो",
        "राम राम",
        "काय म्हणता"
    ],

    # =====================================================
    # HOW ARE YOU
    # =====================================================

    "how_are_you": [

        # English
        "how are you",
        "how are you doing",
        "are you fine",
        "how do you do",

        # Hindi
        "कैसे हो",
        "कैसे हैं",
        "आप कैसे हो",
        "आप कैसे हैं",

        # Marathi
        "तुम्ही कसे आहात",
        "कसा आहेस",
        "कशी आहेस",
        "काय चाललं आहे"
    ],

    # =====================================================
    # THANKS
    # =====================================================

    "thanks": [

        # English
        "thanks",
        "thank you",
        "thanks a lot",

        # Hindi
        "धन्यवाद",
        "शुक्रिया",
        "बहुत धन्यवाद",

        # Marathi
        "धन्यवाद",
        "खूप धन्यवाद"
    ],

    # =====================================================
    # GOODBYE
    # =====================================================

    "goodbye": [

        # English
        "bye",
        "goodbye",
        "see you",
        "see you later",

        # Hindi
        "बाय",
        "फिर मिलेंगे",
        "अलविदा",

        # Marathi
        "पुन्हा भेटू",
        "नंतर भेटू",
        "बाय"
    ],

    # =====================================================
    # HELP
    # =====================================================

    "help": [

        # English
        "help",
        "can you help me",
        "how can you help me",
        "i need help",

        # Hindi
        "मदद",
        "मेरी मदद करो",
        "आप मेरी मदद कर सकते हो",
        "मुझे मदद चाहिए",

        # Marathi
        "मदत",
        "माझी मदत करा",
        "तू मला मदत करू शकतो का",
        "मला मदत हवी आहे"
    ],

    # =====================================================
    # CHATBOT INFO
    # =====================================================

    "chatbot_info": [

        # English
        "what is your name",
        "who are you",
        "tell me your name",

        # Hindi
        "तुम कौन हो",
        "तुम्हारा नाम क्या है",
        "आप कौन हो",

        # Marathi
        "तुझे नाव काय आहे",
        "तू कोण आहेस",
        "तुमचे नाव काय आहे"
    ],

    # =====================================================
    # PERSONAL ASSISTANT
    # =====================================================

    "personal_assistant": [

        # English
        "personal assistant",
        "assistant",
        "virtual assistant",
        "ai assistant",

        # Hindi
        "सहायक",
        "वर्चुअल असिस्टेंट",
        "एआई असिस्टेंट",

        # Marathi
        "वैयक्तिक सहाय्यक",
        "एआय सहाय्यक",
        "व्हर्च्युअल सहाय्यक"
    ]
}









 

# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text: str) -> str:

    text = text.lower().strip()

    text = re.sub(
        r"[^\w\s\u0900-\u097F]",
        "",
        text
    )

    return text

# =========================================================
# DETECT LANGUAGE
# =========================================================

def detect_language(text: str) -> str:

    try:

        lang = detect(text)

        if lang == "mr":
            return "mr"

        elif lang == "hi":
            return "hi"

        else:
            return "en"

    except:
        return "en"

# =========================================================
# DETECT COMMON INTENT
# =========================================================

def detect_common_intent(text: str):

    text = clean_text(text)

    for intent, keywords in COMMON_INTENTS.items():

        for keyword in keywords:

            if keyword.lower() in text:
                return intent

    return None

# =========================================================
# DETECT CATEGORY
# =========================================================


# =========================================================
# MAIN INTENT PREDICTION
# =========================================================

def predict_intent(text: str):

    # =====================================================
    # CLEAN INPUT
    # =====================================================

    cleaned_text = clean_text(text)

    # =====================================================
    # DETECT LANGUAGE
    # =====================================================

    language = detect_language(cleaned_text)

    # =====================================================
    # COMMON INTENT CHECK
    # =====================================================

    common_intent = detect_common_intent(
        cleaned_text
    )

    if common_intent:

        return {
            "intent": common_intent,
            "confidence": 1.0,
            "language": language,
            "category": None
        }

    # =====================================================
    # CATEGORY CHECK
    # =====================================================
 

    # =====================================================
    # ML MODEL PREDICTION
    # =====================================================

    text_vector = vectorizer.transform(
        [cleaned_text]
    )

    pred_idx = model.predict(text_vector)[0]

    pred_label = label_encoder.inverse_transform(
        [pred_idx]
    )[0]

    probabilities = model.predict_proba(
        text_vector
    )[0]

    confidence = max(probabilities)

    # =====================================================
    # RETURN RESPONSE
    # =====================================================

    return {
        "intent": pred_label,
        "confidence": float(confidence),
        "language": language,
        
    }