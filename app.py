
from flask import Flask, render_template, request, jsonify
from lingua import Language, LanguageDetectorBuilder
from uuid import uuid4

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
        "water": "आपकी पेयजल समस्या पर स्थानीय जल आपूर्ति विभाग का ध्यान आवश्यक हो सकता है।",
        "roads": "आपकी सड़क समस्या पर स्थानीय पंचायत या सड़क विभाग का ध्यान आवश्यक हो सकता है।",
        "streetlights": "आपकी स्ट्रीट लाइट की समस्या पर पंचायत या बिजली विभाग का ध्यान आवश्यक हो सकता है।",
        "sanitation": "आपकी सफाई समस्या पर पंचायत या स्वच्छता विभाग का ध्यान आवश्यक हो सकता है।",
        "electricity": "आपकी बिजली समस्या पर स्थानीय बिजली कार्यालय का ध्यान आवश्यक हो सकता है।",
        "unknown": "कृपया पानी, सड़क, स्ट्रीट लाइट, सफाई या बिजली की समस्या बताएं।",
        "disclaimer": "यह केवल एक डेमो है। कोई वास्तविक सरकारी शिकायत दर्ज नहीं हुई है।",
    },
    "Tamil": {
        "water": "உங்கள் குடிநீர் பிரச்சினையை உள்ளூர் நீர் வழங்கல் துறை கவனிக்க வேண்டியிருக்கலாம்.",
        "roads": "உங்கள் சாலைப் பிரச்சினையை உள்ளூர் ஊராட்சி அல்லது சாலைத் துறை கவனிக்க வேண்டியிருக்கலாம்.",
        "streetlights": "உங்கள் தெருவிளக்கு பிரச்சினையை உள்ளூர் ஊராட்சி அல்லது மின்துறை கவனிக்க வேண்டியிருக்கலாம்.",
        "sanitation": "உங்கள் தூய்மை பிரச்சினையை உள்ளூர் ஊராட்சி அல்லது தூய்மைத் துறை கவனிக்க வேண்டியிருக்கலாம்.",
        "electricity": "உங்கள் மின்சாரப் பிரச்சினையை உள்ளூர் மின்வாரியம் கவனிக்க வேண்டியிருக்கலாம்.",
        "unknown": "குடிநீர், சாலை, தெருவிளக்கு, தூய்மை அல்லது மின்சாரப் பிரச்சினையை விவரிக்கவும்.",
        "disclaimer": "இது ஒரு டெமோ மட்டுமே. உண்மையான அரசு புகார் பதிவு செய்யப்படவில்லை.",
    },
    "Telugu": {
        "water": "మీ తాగునీటి సమస్యను స్థానిక నీటి సరఫరా శాఖ పరిశీలించాల్సి ఉండవచ్చు.",
        "roads": "మీ రహదారి సమస్యను స్థానిక పంచాయతీ లేదా రహదారి శాఖ పరిశీలించాల్సి ఉండవచ్చు.",
        "streetlights": "మీ వీధి దీపాల సమస్యను స్థానిక పంచాయతీ లేదా విద్యుత్ శాఖ పరిశీలించాల్సి ఉండవచ్చు.",
        "sanitation": "మీ పారిశుధ్య సమస్యను స్థానిక పంచాయతీ లేదా పారిశుధ్య శాఖ పరిశీలించాల్సి ఉండవచ్చు.",
        "electricity": "మీ విద్యుత్ సమస్యను స్థానిక విద్యుత్ కార్యాలయం పరిశీలించాల్సి ఉండవచ్చు.",
        "unknown": "దయచేసి నీరు, రహదారి, వీధి దీపాలు, పారిశుధ్యం లేదా విద్యుత్ సమస్యను వివరించండి.",
        "disclaimer": "ఇది డెమో మాత్రమే. నిజమైన ప్రభుత్వ ఫిర్యాదు నమోదు కాలేదు.",
    },
    "Marathi": {
        "water": "तुमच्या पिण्याच्या पाण्याच्या समस्येकडे स्थानिक पाणीपुरवठा विभागाने लक्ष देणे आवश्यक असू शकते.",
        "roads": "तुमच्या रस्त्याच्या समस्येकडे स्थानिक ग्रामपंचायत किंवा रस्ते विभागाने लक्ष देणे आवश्यक असू शकते.",
        "streetlights": "तुमच्या पथदिव्यांच्या समस्येकडे ग्रामपंचायत किंवा वीज विभागाने लक्ष देणे आवश्यक असू शकते.",
        "sanitation": "तुमच्या स्वच्छतेच्या समस्येकडे ग्रामपंचायत किंवा स्वच्छता विभागाने लक्ष देणे आवश्यक असू शकते.",
        "electricity": "तुमच्या वीज समस्येकडे स्थानिक वीज कार्यालयाने लक्ष देणे आवश्यक असू शकते.",
        "unknown": "कृपया पाणी, रस्ते, पथदिवे, स्वच्छता किंवा वीज यांपैकी तुमची समस्या सांगा.",
        "disclaimer": "हा फक्त डेमो आहे. वास्तविक सरकारी तक्रार नोंदवली गेलेली नाही.",
    },
}

ISSUES = {
    "water": [
        "drinking water", "water supply", "water", "पानी", "पीने का पानी",
        "குடிநீர்", "தண்ணீர்", "తాగునీరు", "నీరు", "पिण्याचे पाणी", "पाणी",
    ],
    "roads": [
        "pothole", "road", "roads", "सड़क", "गड्ढा", "சாலை",
        "రోడ్డు", "రహదారి", "रस्ता", "खड्डा",
    ],
    "streetlights": [
        "streetlight", "street light", "स्ट्रीट लाइट", "தெருவிளக்கு",
        "వీధి దీపం", "पथदिवा", "पथदिवे",
    ],
    "sanitation": [
        "garbage", "sanitation", "waste", "drain", "कचरा", "सफाई",
        "குப்பை", "கழிவுநீர்", "చెత్త", "పారిశుధ్యం", "स्वच्छता", "गटार",
    ],
    "electricity": [
        "electricity", "power cut", "power outage", "बिजली",
        "மின்சாரம்", "மின்தடை", "విద్యుత్", "కరెంటు", "वीज", "वीजपुरवठा",
    ],
}


def detect_language(message):
    detected = detector.detect_language_of(message)
    return SUPPORTED_LANGUAGES.get(detected, "English")


def classify_issue(message):
    message_lower = message.lower()
    best_issue = None
    best_score = 0

    for issue_id, keywords in ISSUES.items():
        matches = [
            word for word in keywords
            if word.lower() in message_lower
        ]
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