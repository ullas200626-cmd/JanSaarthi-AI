# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
from lingua import Language, LanguageDetectorBuilder
from uuid import uuid4
import re

from database import create_complaint, get_complaint

app = Flask(__name__)

SUPPORTED_LANGUAGES = {
    Language.ENGLISH: "English",
    Language.HINDI: "Hindi",
    Language.TAMIL: "Tamil",
    Language.TELUGU: "Telugu",
    Language.MARATHI: "Marathi",
}

detector = LanguageDetectorBuilder.from_languages(
    *SUPPORTED_LANGUAGES.keys()
).build()

# All text below is stored as real Unicode. Keep this file saved as UTF-8.
TRANSLATIONS = {
    "English": {
        "water": "Your drinking-water issue may need attention from the local water supply department.",
        "roads": "Your road issue may need attention from the local panchayat or road department.",
        "streetlights": "Your streetlight issue may need attention from the local panchayat or electricity department.",
        "sanitation": "Your sanitation issue may need attention from the local panchayat or sanitation department.",
        "electricity": "Your electricity issue may need attention from the local electricity office.",
        "unknown": "Please describe an issue involving water, roads, streetlights, sanitation, or electricity.",
        "disclaimer": "Demo only: no real government complaint has been submitted.",
    },
    "Hindi": {
        "water": "आपकी पेयजल समस्या पर स्थानीय जल आपूर्ति विभाग को ध्यान देने की आवश्यकता हो सकती है।",
        "roads": "आपकी सड़क की समस्या पर स्थानीय पंचायत या सड़क विभाग को ध्यान देने की आवश्यकता हो सकती है।",
        "streetlights": "आपकी स्ट्रीट लाइट की समस्या पर स्थानीय पंचायत या बिजली विभाग को ध्यान देने की आवश्यकता हो सकती है।",
        "sanitation": "आपकी सफाई की समस्या पर स्थानीय पंचायत या स्वच्छता विभाग को ध्यान देने की आवश्यकता हो सकती है।",
        "electricity": "आपकी बिजली की समस्या पर स्थानीय बिजली कार्यालय को ध्यान देने की आवश्यकता हो सकती है।",
        "unknown": "कृपया पानी, सड़क, स्ट्रीट लाइट, सफाई या बिजली से जुड़ी समस्या बताएं।",
        "disclaimer": "केवल डेमो: आपकी शिकायत किसी सरकारी विभाग को नहीं भेजी गई है।",
    },
    "Tamil": {
        "water": "உங்கள் குடிநீர் பிரச்சினையை உள்ளூர் குடிநீர் வழங்கல் துறை கவனிக்க வேண்டியிருக்கலாம்.",
        "roads": "உங்கள் சாலைப் பிரச்சினையை உள்ளூர் ஊராட்சி அல்லது சாலைத் துறை கவனிக்க வேண்டியிருக்கலாம்.",
        "streetlights": "உங்கள் தெருவிளக்கு பிரச்சினையை உள்ளூர் ஊராட்சி அல்லது மின்துறை கவனிக்க வேண்டியிருக்கலாம்.",
        "sanitation": "உங்கள் தூய்மை பிரச்சினையை உள்ளூர் ஊராட்சி அல்லது சுகாதாரத் துறை கவனிக்க வேண்டியிருக்கலாம்.",
        "electricity": "உங்கள் மின்சாரப் பிரச்சினையை உள்ளூர் மின்சார அலுவலகம் கவனிக்க வேண்டியிருக்கலாம்.",
        "unknown": "தண்ணீர், சாலை, தெருவிளக்கு, தூய்மை அல்லது மின்சாரம் தொடர்பான பிரச்சினையை விவரிக்கவும்.",
        "disclaimer": "இது ஒரு டெமோ மட்டுமே: உண்மையான அரசு புகார் எதுவும் அனுப்பப்படவில்லை.",
    },
    "Telugu": {
        "water": "మీ తాగునీటి సమస్యపై స్థానిక నీటి సరఫరా శాఖ దృష్టి పెట్టాల్సి ఉండవచ్చు.",
        "roads": "మీ రహదారి సమస్యపై స్థానిక పంచాయతీ లేదా రహదారుల శాఖ దృష్టి పెట్టాల్సి ఉండవచ్చు.",
        "streetlights": "మీ వీధి దీపాల సమస్యపై స్థానిక పంచాయతీ లేదా విద్యుత్ శాఖ దృష్టి పెట్టాల్సి ఉండవచ్చు.",
        "sanitation": "మీ పారిశుధ్య సమస్యపై స్థానిక పంచాయతీ లేదా పారిశుధ్య శాఖ దృష్టి పెట్టాల్సి ఉండవచ్చు.",
        "electricity": "మీ విద్యుత్ సమస్యపై స్థానిక విద్యుత్ కార్యాలయం దృష్టి పెట్టాల్సి ఉండవచ్చు.",
        "unknown": "దయచేసి నీరు, రహదారులు, వీధి దీపాలు, పారిశుధ్యం లేదా విద్యుత్ సమస్యను వివరించండి.",
        "disclaimer": "ఇది డెమో మాత్రమే: నిజమైన ప్రభుత్వ ఫిర్యాదు పంపబడలేదు.",
    },
    "Marathi": {
        "water": "तुमच्या पिण्याच्या पाण्याच्या समस्येकडे स्थानिक पाणीपुरवठा विभागाने लक्ष देण्याची गरज असू शकते.",
        "roads": "तुमच्या रस्त्याच्या समस्येकडे स्थानिक पंचायत किंवा रस्ते विभागाने लक्ष देण्याची गरज असू शकते.",
        "streetlights": "तुमच्या पथदिव्यांच्या समस्येकडे स्थानिक पंचायत किंवा वीज विभागाने लक्ष देण्याची गरज असू शकते.",
        "sanitation": "तुमच्या स्वच्छतेच्या समस्येकडे स्थानिक पंचायत किंवा स्वच्छता विभागाने लक्ष देण्याची गरज असू शकते.",
        "electricity": "तुमच्या वीज समस्येकडे स्थानिक वीज कार्यालयाने लक्ष देण्याची गरज असू शकते.",
        "unknown": "कृपया पाणी, रस्ते, पथदिवे, स्वच्छता किंवा वीज यासंबंधीची समस्या सांगा.",
        "disclaimer": "फक्त डेमो: कोणतीही खरी सरकारी तक्रार पाठवलेली नाही.",
    },
}

# English keywords plus common native-script and Romanized words.
ISSUES = {
    "water": [
        "drinking water", "water supply", "water", "pothole water",
        "पानी", "पेयजल", "नल में पानी", "पाणी", "पाण्याची", "पाणीपुरवठा",
       "தண்ணீர்", "குடிநீர்",
"నీరు", "తాగునీరు", "నీళ్లు", "నీళ్లు రావడం లేదు",
"నీళ్లు రావడం", "నీటి సరఫరా", "నీరు రావడం లేదు",
        "pani", "paanee", "paani", "water problem", "no water",
    ],
    "roads": [
        "pothole", "road", "roads", "ರಸ್ತೆ",
        "सड़क", "सडक", "रस्ता", "रस्ते", "சாலை", "రోడ్డు", "రహదారి",
        "sadak", "sarak", "rasta", "road problem", "bad road",
    ],
    "streetlights": [
        "streetlight", "street light", "street lights", "street lamp",
        "स्ट्रीट लाइट", "सड़क की बत्ती", "पथदिवे", "தெருவிளக்கு", "వీధి దీపాలు",
        "streetlight not working", "street light not working",
    ],
    "sanitation": [
        "garbage", "sanitation", "waste", "drain", "drainage", "sewage",
        "कचरा", "सफाई", "स्वच्छता", "कचरा", "कचरा समस्या",
        "குப்பை", "சுத்தம்", "చెత్త", "పారిశుధ్యం", "कचरा", "घाण",
        "kachra", "kacra", "garbage problem", "dirty street",
    ],
    "electricity": [
        "electricity", "power cut", "power outage", "no power", "current",
        "बिजली", "बिजली नहीं", "वीज", "वीज नाही", "மின்சாரம்", "மின்தடை",
        "విద్యుత్", "కరెంట్", "bijli", "bijalee", "light gone", "no electricity",
    ],
}

ROMANIZED_LANGUAGE_HINTS = {
    "Hindi": [
        "pani", "paani", "sadak", "bijli", "kachra", "safai", "nahi", "hai",
        "kripya", "shikayat",
    ],
    "Marathi": ["paani", "rasta", "vij", "nahi", "kachra", "swachhata"],
    "Tamil": ["thanneer", "saalai", "minsaara", "kuppai"],
    "Telugu": ["neeru", "roaddu", "karentu", "chetta"],
}

MARATHI_HINTS = ["पाणी", "रस्ता", "वीज", "नाही", "स्वच्छता"]
TAMIL_HINTS = ["தண்ணீர்", "குடிநீர்", "சாலை", "மின்சாரம்", "குப்பை"]
TELUGU_HINTS = ["నీరు", "రహదారి", "విద్యుత్", "చెత్త", "కరెంట్"]


def detect_language(message):
    """Detect native scripts first, then common Romanized civic words."""
    text = message.strip()
    if any("\u0B80" <= ch <= "\u0BFF" for ch in text):
        return "Tamil"
    if any("\u0C00" <= ch <= "\u0C7F" for ch in text):
        return "Telugu"
    if any(term in text for term in MARATHI_HINTS):
        return "Marathi"
    if any("\u0900" <= ch <= "\u097F" for ch in text):
        return "Hindi"

    lower = re.sub(r"[^a-z\s]", " ", text.lower())
    words = set(lower.split())
    # Prefer a distinctive language match. Hindi is the fallback for common
    # Romanized Hindi words such as "pani" and "bijli".
    for language in ("Tamil", "Telugu", "Marathi"):
        if any(term in lower for term in ROMANIZED_LANGUAGE_HINTS[language]):
            return language
    if any(term in lower for term in ROMANIZED_LANGUAGE_HINTS["Hindi"]):
        return "Hindi"

    detected = detector.detect_language_of(text)
    return SUPPORTED_LANGUAGES.get(detected, "English")


def classify_issue(message):
    message_lower = message.casefold()
    best_issue = None
    best_score = 0

    for issue_id, keywords in ISSUES.items():
        matches = [word for word in keywords if word.casefold() in message_lower]
        if matches:
            score = max(len(word) for word in matches)
            if score > best_score:
                best_score = score
                best_issue = issue_id

    return best_issue


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "project": "JanSaarthi AI",
        "supported_languages": list(SUPPORTED_LANGUAGES.values()),
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Please enter your civic issue."}), 400

    language = detect_language(message)
    issue = classify_issue(message)
    translations = TRANSLATIONS[language]

    reply = translations[issue] if issue else translations["unknown"]
    reply += "\n\n" + translations["disclaimer"]

    return jsonify({
        "reply": reply,
        "language": language,
        "issue": issue,
    })


@app.route("/api/complaints", methods=["POST"])
def register_complaint():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    issue = str(data.get("issue", "")).strip()
    language = str(data.get("language", "English")).strip()

    if not message or issue not in ISSUES:
        return jsonify({
            "error": "Please submit a message with a recognized civic issue."
        }), 400

    if language not in TRANSLATIONS:
        language = "English"

    complaint_id = "JS-" + uuid4().hex[:8].upper()

    create_complaint(
        complaint_id=complaint_id,
        issue=issue,
        message=message,
        language=language,
    )

    complaint = get_complaint(complaint_id)

    return jsonify({
        "success": True,
        "demo": True,
        "complaint": dict(complaint),
        "notice": "Demo record only. This complaint was not sent to a government department.",
    }), 201


@app.route("/api/complaints/<complaint_id>", methods=["GET"])
def track_complaint(complaint_id):
    complaint = get_complaint(complaint_id.strip().upper())

    if complaint is None:
        return jsonify({
            "error": "No demo complaint was found with that ID."
        }), 404

    return jsonify({
        "success": True,
        "demo": True,
        "complaint": dict(complaint),
        "notice": "Demo status only. No live government system is connected.",
    })


if __name__ == "__main__":
    app.run(debug=True)
