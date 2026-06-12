 
import json
import os

from typing import List, Optional, Dict

from rapidfuzz import fuzz

# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

SERVICES_FILE = os.path.join(
    BASE_DIR,
    "data",
    "services.json"
)

# =========================================================
# CATEGORY KEYWORDS
# =========================================================

CATEGORY_KEYWORDS = {

    "hospital": [
        "hospital",
        "hospitals",
        "clinic",
        "doctor",
        "medical",

        "अस्पताल",
        "हॉस्पिटल",
        "रुग्णालय",
        "दवाखाना"
    ],

    "school": [
        "school",
        "schools",
        "academy",

        "स्कूल",
        "विद्यालय",
        "शाळा"
    ],

    "college": [
        "college",
        "engineering college",
        "medical college",
        "university",

        "कॉलेज",
        "महाविद्यालय",
        "विद्यापीठ"
    ],

    "pharmacy": [
        "pharmacy",
        "medical store",
        "chemist",
        "medicine",
        "farmacy",

        "फार्मसी",
        "मेडिकल",
        "औषध दुकान"
    ],

    "hotel": [
        "hotel",
        "restaurant",
        "lodge",

        "होटल",
        "हॉटेल"
    ],

    "bank": [
        "bank",
        "banks",
        "atm",

        "बैंक",
        "बँक",
        "एटीएम"
    ],

    "police_station": [
        "police",
        "police station",

        "पोलीस",
        "पुलिस",
        "पोलीस स्टेशन"
    ]
}

# =========================================================
# LOAD SERVICES
# =========================================================

def load_services() -> List[Dict]:

    try:

        with open(
            SERVICES_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception as e:

        print("Service loading error:", e)

        return []

# =========================================================
# DETECT CATEGORY
# =========================================================

def detect_category(text: str) -> Optional[str]:

    text_lower = text.lower().strip()

    # =====================================================
    # EXACT MATCH
    # =====================================================

    for category, keywords in CATEGORY_KEYWORDS.items():

        for keyword in keywords:

            if keyword.lower() in text_lower:
                return category

    # =====================================================
    # FUZZY MATCH
    # =====================================================

    best_category = None

    best_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():

        for keyword in keywords:

            score = fuzz.partial_ratio(
                text_lower,
                keyword.lower()
            )

            if score > best_score:

                best_score = score

                best_category = category

    if best_score >= 88:
        return best_category

    return None

# =========================================================
# GET SERVICES BY CATEGORY
# =========================================================

def get_services_by_category(
    category: str,
    limit: int = 10
) -> List[Dict]:

    services = load_services()

    filtered = [

        item for item in services

        if item["category"] == category
    ]

    return filtered[:limit]

# =========================================================
# GET SERVICE BY NAME
# =========================================================

def get_service_by_name(
    query: str
) -> Optional[Dict]:

    services = load_services()

    query_lower = query.lower().strip()

    # =====================================================
    # EXACT MATCH
    # =====================================================

    for item in services:

        service_name = item["name"].lower()

        if (
            service_name in query_lower
            or query_lower in service_name
        ):

            return item

    # =====================================================
    # FUZZY MATCH
    # =====================================================

    best_item = None

    best_score = 0

    for item in services:

        score = fuzz.partial_ratio(
            query_lower,
            item["name"].lower()
        )

        if score > best_score:

            best_score = score

            best_item = item

    if best_score >= 88:
        return best_item

    return None

# =========================================================
# FORMAT SERVICE LIST
# =========================================================

def format_service_list(
    category: str,
    services: List[Dict],
    language: str = "en"
) -> str:

    if not services:

        return "No services found."

    # =====================================================
    # MULTILINGUAL TITLES
    # =====================================================

    if language == "hi":

        title = f"📌 यहाँ कुछ {category} विकल्प हैं:\n"

        suggestion = "💡 आप यह भी पूछ सकते हैं:"

    elif language == "mr":

        title = f"📌 येथे काही {category} पर्याय आहेत:\n"

        suggestion = "💡 तुम्ही हे देखील विचारू शकता:"

    else:

        title = f"📌 Here are some {category} options:\n"

        suggestion = "💡 You can also ask:"

    lines = [title]

    # =====================================================
    # SERVICE ITEMS
    # =====================================================

    for idx, item in enumerate(services, start=1):

        lines.append(

            f"{idx}. 🏢 {item['name']}\n"
            f"📍 Address: {item['address']}\n"
        )

    # =====================================================
    # SUGGESTIONS
    # =====================================================

    sample = services[0]["name"]

    lines.append(suggestion)

    lines.append(f"• Address of {sample}")

    lines.append(f"• Phone number of {sample}")

    lines.append(f"• Location of {sample}")

    return "\n".join(lines)


# =========================================================
# FORMAT SERVICE DETAILS
# =========================================================

def format_service_details(
    service: Dict,
    language: str = "en"
) -> str:

    # =====================================================
    # HINDI
    # =====================================================

    if language == "hi":

        return (

            f"🏢 {service['name']}\n"
            f"📂 श्रेणी: {service['category']}\n"
            f"📍 पता: {service['address']}\n"
            f"📞 फोन: {service['phone']}\n"
            f"🗺 स्थान: {service['location']}"
        )

    # =====================================================
    # MARATHI
    # =====================================================

    elif language == "mr":

        return (

            f"🏢 {service['name']}\n"
            f"📂 प्रकार: {service['category']}\n"
            f"📍 पत्ता: {service['address']}\n"
            f"📞 फोन: {service['phone']}\n"
            f"🗺 स्थान: {service['location']}"
        )

    # =====================================================
    # ENGLISH
    # =====================================================

    else:

        return (

            f"🏢 {service['name']}\n"
            f"📂 Category: {service['category']}\n"
            f"📍 Address: {service['address']}\n"
            f"📞 Phone: {service['phone']}\n"
            f"🗺 Location: {service['location']}"
        )
 