import json
import os
from typing import List, Optional, Dict
from rapidfuzz import fuzz


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICES_FILE = os.path.join(BASE_DIR, "data", "services.json")


CATEGORY_KEYWORDS = {
    "hospital": [
        "hospital", "hospitals", "clinic", "medical", "doctor", "emergency",
        "अस्पताल", "हॉस्पिटल", "रुग्णालय", "डॉक्टर", "क्लिनिक"
    ],
    "school": [
        "school", "schools", "education", "academy",
        "school list", "विद्यालय", "शाळा", "स्कूल"
    ],
    "bank": [
        "bank", "banks", "atm", "finance",
        "बैंक", "बँक", "एटीएम"
    ],
    "police_station": [
        "police", "police station", "station", "thana",
        "पोलीस", "पुलिस", "थाना", "पोलीस स्टेशन"
    ],
    "hotel": [
        "hotel", "hotels", "stay", "lodge", "restaurant",
        "होटल", "हॉटेल", "लॉज"
    ],
    "pharmacy": [
        "pharmacy", "medical store", "medicine", "chemist", "drug store",
        "फार्मेसी", "मेडिकल", "औषध दुकान", "केमिस्ट"
    ]
}


def load_services() -> List[Dict]:
    with open(SERVICES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_category(text: str) -> Optional[str]:
    text_lower = text.lower().strip()

    # Exact keyword match first
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return category

    # Fuzzy match second
    best_category = None
    best_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            score = fuzz.partial_ratio(text_lower, keyword.lower())
            if score > best_score:
                best_score = score
                best_category = category

    if best_score >= 75:
        return best_category

    return None


def get_services_by_category(category: str) -> List[Dict]:
    services = load_services()
    return [item for item in services if item["category"] == category]


def get_service_by_name(query: str) -> Optional[Dict]:
    services = load_services()
    query_lower = query.lower().strip()

    # Exact contains
    for item in services:
        if item["name"].lower() in query_lower or query_lower in item["name"].lower():
            return item

    # Fuzzy
    best_item = None
    best_score = 0

    for item in services:
        score = fuzz.partial_ratio(query_lower, item["name"].lower())
        if score > best_score:
            best_score = score
            best_item = item

    if best_score >= 75:
        return best_item

    return None


def format_service_list(category: str, services: List[Dict]) -> str:
    if not services:
        return f"Sorry, I could not find any {category.replace('_', ' ')} right now."

    lines = [f"Here are some {category.replace('_', ' ')} options:"]
    for idx, item in enumerate(services, start=1):
        lines.append(f"{idx}. {item['name']} - {item['address']}")

    lines.append("\nYou can ask for details like:")
    lines.append(f"- address of {services[0]['name']}")
    lines.append(f"- phone number of {services[0]['name']}")
    lines.append(f"- location of {services[0]['name']}")

    return "\n".join(lines)


def format_service_details(service: Dict) -> str:
    return (
        f"{service['name']}\n"
        f"Category: {service['category'].replace('_', ' ').title()}\n"
        f"Address: {service['address']}\n"
        f"Phone: {service['phone']}\n"
        f"Location: {service['location']}"
    )