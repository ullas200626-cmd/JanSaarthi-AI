
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
        "water": "αñåαñ¬αñòαÑÇ αñ¬αÑçαñ»αñ£αñ▓ αñ╕αñ«αñ╕αÑìαñ»αñ╛ αñ¬αñ░ αñ╕αÑìαñÑαñ╛αñ¿αÑÇαñ» αñ£αñ▓ αñåαñ¬αÑéαñ░αÑìαññαñ┐ αñ╡αñ┐αñ¡αñ╛αñù αñòαñ╛ αñºαÑìαñ»αñ╛αñ¿ αñåαñ╡αñ╢αÑìαñ»αñò αñ╣αÑï αñ╕αñòαññαñ╛ αñ╣αÑêαÑñ",
        "roads": "αñåαñ¬αñòαÑÇ αñ╕αñíαñ╝αñò αñ╕αñ«αñ╕αÑìαñ»αñ╛ αñ¬αñ░ αñ╕αÑìαñÑαñ╛αñ¿αÑÇαñ» αñ¬αñéαñÜαñ╛αñ»αññ αñ»αñ╛ αñ╕αñíαñ╝αñò αñ╡αñ┐αñ¡αñ╛αñù αñòαñ╛ αñºαÑìαñ»αñ╛αñ¿ αñåαñ╡αñ╢αÑìαñ»αñò αñ╣αÑï αñ╕αñòαññαñ╛ αñ╣αÑêαÑñ",
        "streetlights": "αñåαñ¬αñòαÑÇ αñ╕αÑìαñƒαÑìαñ░αÑÇαñƒ αñ▓αñ╛αñçαñƒ αñòαÑÇ αñ╕αñ«αñ╕αÑìαñ»αñ╛ αñ¬αñ░ αñ¬αñéαñÜαñ╛αñ»αññ αñ»αñ╛ αñ¼αñ┐αñ£αñ▓αÑÇ αñ╡αñ┐αñ¡αñ╛αñù αñòαñ╛ αñºαÑìαñ»αñ╛αñ¿ αñåαñ╡αñ╢αÑìαñ»αñò αñ╣αÑï αñ╕αñòαññαñ╛ αñ╣αÑêαÑñ",
        "sanitation": "αñåαñ¬αñòαÑÇ αñ╕αñ½αñ╛αñê αñ╕αñ«αñ╕αÑìαñ»αñ╛ αñ¬αñ░ αñ¬αñéαñÜαñ╛αñ»αññ αñ»αñ╛ αñ╕αÑìαñ╡αñÜαÑìαñ¢αññαñ╛ αñ╡αñ┐αñ¡αñ╛αñù αñòαñ╛ αñºαÑìαñ»αñ╛αñ¿ αñåαñ╡αñ╢αÑìαñ»αñò αñ╣αÑï αñ╕αñòαññαñ╛ αñ╣αÑêαÑñ",
        "electricity": "αñåαñ¬αñòαÑÇ αñ¼αñ┐αñ£αñ▓αÑÇ αñ╕αñ«αñ╕αÑìαñ»αñ╛ αñ¬αñ░ αñ╕αÑìαñÑαñ╛αñ¿αÑÇαñ» αñ¼αñ┐αñ£αñ▓αÑÇ αñòαñ╛αñ░αÑìαñ»αñ╛αñ▓αñ» αñòαñ╛ αñºαÑìαñ»αñ╛αñ¿ αñåαñ╡αñ╢αÑìαñ»αñò αñ╣αÑï αñ╕αñòαññαñ╛ αñ╣αÑêαÑñ",
        "unknown": "αñòαÑâαñ¬αñ»αñ╛ αñ¬αñ╛αñ¿αÑÇ, αñ╕αñíαñ╝αñò, αñ╕αÑìαñƒαÑìαñ░αÑÇαñƒ αñ▓αñ╛αñçαñƒ, αñ╕αñ½αñ╛αñê αñ»αñ╛ αñ¼αñ┐αñ£αñ▓αÑÇ αñòαÑÇ αñ╕αñ«αñ╕αÑìαñ»αñ╛ αñ¼αññαñ╛αñÅαñéαÑñ",
        "disclaimer": "αñ»αñ╣ αñòαÑçαñ╡αñ▓ αñÅαñò αñíαÑçαñ«αÑï αñ╣αÑêαÑñ αñòαÑïαñê αñ╡αñ╛αñ╕αÑìαññαñ╡αñ┐αñò αñ╕αñ░αñòαñ╛αñ░αÑÇ αñ╢αñ┐αñòαñ╛αñ»αññ αñªαñ░αÑìαñ£ αñ¿αñ╣αÑÇαñé αñ╣αÑüαñê αñ╣αÑêαÑñ",
    },
    "Tamil": {
        "water": "α«ëα«Öα»ìα«òα«│α»ì α«òα»üα«ƒα«┐α«¿α»Çα«░α»ì α«¬α«┐α«░α«Üα»ìα«Üα«┐α«⌐α»êα«»α»ê α«ëα«│α»ìα«│α»éα«░α»ì α«¿α»Çα«░α»ì α«╡α«┤α«Öα»ìα«òα«▓α»ì α«ñα»üα«▒α»ê α«òα«╡α«⌐α«┐α«òα»ìα«ò α«╡α»çα«úα»ìα«ƒα«┐α«»α«┐α«░α»üα«òα»ìα«òα«▓α«╛α««α»ì.",
        "roads": "α«ëα«Öα»ìα«òα«│α»ì α«Üα«╛α«▓α»êα«¬α»ì α«¬α«┐α«░α«Üα»ìα«Üα«┐α«⌐α»êα«»α»ê α«ëα«│α»ìα«│α»éα«░α»ì α«èα«░α«╛α«ƒα»ìα«Üα«┐ α«àα«▓α»ìα«▓α«ñα»ü α«Üα«╛α«▓α»êα«ñα»ì α«ñα»üα«▒α»ê α«òα«╡α«⌐α«┐α«òα»ìα«ò α«╡α»çα«úα»ìα«ƒα«┐α«»α«┐α«░α»üα«òα»ìα«òα«▓α«╛α««α»ì.",
        "streetlights": "α«ëα«Öα»ìα«òα«│α»ì α«ñα»åα«░α»üα«╡α«┐α«│α«òα»ìα«òα»ü α«¬α«┐α«░α«Üα»ìα«Üα«┐α«⌐α»êα«»α»ê α«ëα«│α»ìα«│α»éα«░α»ì α«èα«░α«╛α«ƒα»ìα«Üα«┐ α«àα«▓α»ìα«▓α«ñα»ü α««α«┐α«⌐α»ìα«ñα»üα«▒α»ê α«òα«╡α«⌐α«┐α«òα»ìα«ò α«╡α»çα«úα»ìα«ƒα«┐α«»α«┐α«░α»üα«òα»ìα«òα«▓α«╛α««α»ì.",
        "sanitation": "α«ëα«Öα»ìα«òα«│α»ì α«ñα»éα«»α»ìα««α»ê α«¬α«┐α«░α«Üα»ìα«Üα«┐α«⌐α»êα«»α»ê α«ëα«│α»ìα«│α»éα«░α»ì α«èα«░α«╛α«ƒα»ìα«Üα«┐ α«àα«▓α»ìα«▓α«ñα»ü α«ñα»éα«»α»ìα««α»êα«ñα»ì α«ñα»üα«▒α»ê α«òα«╡α«⌐α«┐α«òα»ìα«ò α«╡α»çα«úα»ìα«ƒα«┐α«»α«┐α«░α»üα«òα»ìα«òα«▓α«╛α««α»ì.",
        "electricity": "α«ëα«Öα»ìα«òα«│α»ì α««α«┐α«⌐α»ìα«Üα«╛α«░α«¬α»ì α«¬α«┐α«░α«Üα»ìα«Üα«┐α«⌐α»êα«»α»ê α«ëα«│α»ìα«│α»éα«░α»ì α««α«┐α«⌐α»ìα«╡α«╛α«░α«┐α«»α««α»ì α«òα«╡α«⌐α«┐α«òα»ìα«ò α«╡α»çα«úα»ìα«ƒα«┐α«»α«┐α«░α»üα«òα»ìα«òα«▓α«╛α««α»ì.",
        "unknown": "α«òα»üα«ƒα«┐α«¿α»Çα«░α»ì, α«Üα«╛α«▓α»ê, α«ñα»åα«░α»üα«╡α«┐α«│α«òα»ìα«òα»ü, α«ñα»éα«»α»ìα««α»ê α«àα«▓α»ìα«▓α«ñα»ü α««α«┐α«⌐α»ìα«Üα«╛α«░α«¬α»ì α«¬α«┐α«░α«Üα»ìα«Üα«┐α«⌐α»êα«»α»ê α«╡α«┐α«╡α«░α«┐α«òα»ìα«òα«╡α»üα««α»ì.",
        "disclaimer": "α«çα«ñα»ü α«Æα«░α»ü α«ƒα»åα««α»ï α««α«ƒα»ìα«ƒα»üα««α»ç. α«ëα«úα»ìα««α»êα«»α«╛α«⌐ α«àα«░α«Üα»ü α«¬α»üα«òα«╛α«░α»ì α«¬α«ñα«┐α«╡α»ü α«Üα»åα«»α»ìα«»α«¬α»ìα«¬α«ƒα«╡α«┐α«▓α»ìα«▓α»ê.",
    },
    "Telugu": {
        "water": "α░«α▒Ç α░ñα░╛α░ùα▒üα░¿α▒Çα░ƒα░┐ α░╕α░«α░╕α▒ìα░»α░¿α▒ü α░╕α▒ìα░Ñα░╛α░¿α░┐α░ò α░¿α▒Çα░ƒα░┐ α░╕α░░α░½α░░α░╛ α░╢α░╛α░û α░¬α░░α░┐α░╢α▒Çα░▓α░┐α░éα░Üα░╛α░▓α▒ìα░╕α░┐ α░ëα░éα░íα░╡α░Üα▒ìα░Üα▒ü.",
        "roads": "α░«α▒Ç α░░α░╣α░ªα░╛α░░α░┐ α░╕α░«α░╕α▒ìα░»α░¿α▒ü α░╕α▒ìα░Ñα░╛α░¿α░┐α░ò α░¬α░éα░Üα░╛α░»α░ñα▒Ç α░▓α▒çα░ªα░╛ α░░α░╣α░ªα░╛α░░α░┐ α░╢α░╛α░û α░¬α░░α░┐α░╢α▒Çα░▓α░┐α░éα░Üα░╛α░▓α▒ìα░╕α░┐ α░ëα░éα░íα░╡α░Üα▒ìα░Üα▒ü.",
        "streetlights": "α░«α▒Ç α░╡α▒Çα░ºα░┐ α░ªα▒Çα░¬α░╛α░▓ α░╕α░«α░╕α▒ìα░»α░¿α▒ü α░╕α▒ìα░Ñα░╛α░¿α░┐α░ò α░¬α░éα░Üα░╛α░»α░ñα▒Ç α░▓α▒çα░ªα░╛ α░╡α░┐α░ªα▒ìα░»α▒üα░ñα▒ì α░╢α░╛α░û α░¬α░░α░┐α░╢α▒Çα░▓α░┐α░éα░Üα░╛α░▓α▒ìα░╕α░┐ α░ëα░éα░íα░╡α░Üα▒ìα░Üα▒ü.",
        "sanitation": "α░«α▒Ç α░¬α░╛α░░α░┐α░╢α▒üα░ºα▒ìα░» α░╕α░«α░╕α▒ìα░»α░¿α▒ü α░╕α▒ìα░Ñα░╛α░¿α░┐α░ò α░¬α░éα░Üα░╛α░»α░ñα▒Ç α░▓α▒çα░ªα░╛ α░¬α░╛α░░α░┐α░╢α▒üα░ºα▒ìα░» α░╢α░╛α░û α░¬α░░α░┐α░╢α▒Çα░▓α░┐α░éα░Üα░╛α░▓α▒ìα░╕α░┐ α░ëα░éα░íα░╡α░Üα▒ìα░Üα▒ü.",
        "electricity": "α░«α▒Ç α░╡α░┐α░ªα▒ìα░»α▒üα░ñα▒ì α░╕α░«α░╕α▒ìα░»α░¿α▒ü α░╕α▒ìα░Ñα░╛α░¿α░┐α░ò α░╡α░┐α░ªα▒ìα░»α▒üα░ñα▒ì α░òα░╛α░░α▒ìα░»α░╛α░▓α░»α░é α░¬α░░α░┐α░╢α▒Çα░▓α░┐α░éα░Üα░╛α░▓α▒ìα░╕α░┐ α░ëα░éα░íα░╡α░Üα▒ìα░Üα▒ü.",
        "unknown": "α░ªα░»α░Üα▒çα░╕α░┐ α░¿α▒Çα░░α▒ü, α░░α░╣α░ªα░╛α░░α░┐, α░╡α▒Çα░ºα░┐ α░ªα▒Çα░¬α░╛α░▓α▒ü, α░¬α░╛α░░α░┐α░╢α▒üα░ºα▒ìα░»α░é α░▓α▒çα░ªα░╛ α░╡α░┐α░ªα▒ìα░»α▒üα░ñα▒ì α░╕α░«α░╕α▒ìα░»α░¿α▒ü α░╡α░┐α░╡α░░α░┐α░éα░Üα░éα░íα░┐.",
        "disclaimer": "α░çα░ªα░┐ α░íα▒åα░«α▒ï α░«α░╛α░ñα▒ìα░░α░«α▒ç. α░¿α░┐α░£α░«α▒êα░¿ α░¬α▒ìα░░α░¡α▒üα░ñα▒ìα░╡ α░½α░┐α░░α▒ìα░»α░╛α░ªα▒ü α░¿α░«α▒ïα░ªα▒ü α░òα░╛α░▓α▒çα░ªα▒ü.",
    },
    "Marathi": {
        "water": "αññαÑüαñ«αñÜαÑìαñ»αñ╛ αñ¬αñ┐αñúαÑìαñ»αñ╛αñÜαÑìαñ»αñ╛ αñ¬αñ╛αñúαÑìαñ»αñ╛αñÜαÑìαñ»αñ╛ αñ╕αñ«αñ╕αÑìαñ»αÑçαñòαñíαÑç αñ╕αÑìαñÑαñ╛αñ¿αñ┐αñò αñ¬αñ╛αñúαÑÇαñ¬αÑüαñ░αñ╡αñáαñ╛ αñ╡αñ┐αñ¡αñ╛αñùαñ╛αñ¿αÑç αñ▓αñòαÑìαñ╖ αñªαÑçαñúαÑç αñåαñ╡αñ╢αÑìαñ»αñò αñàαñ╕αÑé αñ╢αñòαññαÑç.",
        "roads": "αññαÑüαñ«αñÜαÑìαñ»αñ╛ αñ░αñ╕αÑìαññαÑìαñ»αñ╛αñÜαÑìαñ»αñ╛ αñ╕αñ«αñ╕αÑìαñ»αÑçαñòαñíαÑç αñ╕αÑìαñÑαñ╛αñ¿αñ┐αñò αñùαÑìαñ░αñ╛αñ«αñ¬αñéαñÜαñ╛αñ»αññ αñòαñ┐αñéαñ╡αñ╛ αñ░αñ╕αÑìαññαÑç αñ╡αñ┐αñ¡αñ╛αñùαñ╛αñ¿αÑç αñ▓αñòαÑìαñ╖ αñªαÑçαñúαÑç αñåαñ╡αñ╢αÑìαñ»αñò αñàαñ╕αÑé αñ╢αñòαññαÑç.",
        "streetlights": "αññαÑüαñ«αñÜαÑìαñ»αñ╛ αñ¬αñÑαñªαñ┐αñ╡αÑìαñ»αñ╛αñéαñÜαÑìαñ»αñ╛ αñ╕αñ«αñ╕αÑìαñ»αÑçαñòαñíαÑç αñùαÑìαñ░αñ╛αñ«αñ¬αñéαñÜαñ╛αñ»αññ αñòαñ┐αñéαñ╡αñ╛ αñ╡αÑÇαñ£ αñ╡αñ┐αñ¡αñ╛αñùαñ╛αñ¿αÑç αñ▓αñòαÑìαñ╖ αñªαÑçαñúαÑç αñåαñ╡αñ╢αÑìαñ»αñò αñàαñ╕αÑé αñ╢αñòαññαÑç.",
        "sanitation": "αññαÑüαñ«αñÜαÑìαñ»αñ╛ αñ╕αÑìαñ╡αñÜαÑìαñ¢αññαÑçαñÜαÑìαñ»αñ╛ αñ╕αñ«αñ╕αÑìαñ»αÑçαñòαñíαÑç αñùαÑìαñ░αñ╛αñ«αñ¬αñéαñÜαñ╛αñ»αññ αñòαñ┐αñéαñ╡αñ╛ αñ╕αÑìαñ╡αñÜαÑìαñ¢αññαñ╛ αñ╡αñ┐αñ¡αñ╛αñùαñ╛αñ¿αÑç αñ▓αñòαÑìαñ╖ αñªαÑçαñúαÑç αñåαñ╡αñ╢αÑìαñ»αñò αñàαñ╕αÑé αñ╢αñòαññαÑç.",
        "electricity": "αññαÑüαñ«αñÜαÑìαñ»αñ╛ αñ╡αÑÇαñ£ αñ╕αñ«αñ╕αÑìαñ»αÑçαñòαñíαÑç αñ╕αÑìαñÑαñ╛αñ¿αñ┐αñò αñ╡αÑÇαñ£ αñòαñ╛αñ░αÑìαñ»αñ╛αñ▓αñ»αñ╛αñ¿αÑç αñ▓αñòαÑìαñ╖ αñªαÑçαñúαÑç αñåαñ╡αñ╢αÑìαñ»αñò αñàαñ╕αÑé αñ╢αñòαññαÑç.",
        "unknown": "αñòαÑâαñ¬αñ»αñ╛ αñ¬αñ╛αñúαÑÇ, αñ░αñ╕αÑìαññαÑç, αñ¬αñÑαñªαñ┐αñ╡αÑç, αñ╕αÑìαñ╡αñÜαÑìαñ¢αññαñ╛ αñòαñ┐αñéαñ╡αñ╛ αñ╡αÑÇαñ£ αñ»αñ╛αñéαñ¬αÑêαñòαÑÇ αññαÑüαñ«αñÜαÑÇ αñ╕αñ«αñ╕αÑìαñ»αñ╛ αñ╕αñ╛αñéαñùαñ╛.",
        "disclaimer": "αñ╣αñ╛ αñ½αñòαÑìαññ αñíαÑçαñ«αÑï αñåαñ╣αÑç. αñ╡αñ╛αñ╕αÑìαññαñ╡αñ┐αñò αñ╕αñ░αñòαñ╛αñ░αÑÇ αññαñòαÑìαñ░αñ╛αñ░ αñ¿αÑïαñéαñªαñ╡αñ▓αÑÇ αñùαÑçαñ▓αÑçαñ▓αÑÇ αñ¿αñ╛αñ╣αÑÇ.",
    },
}

ISSUES = {
    "water": [
        "drinking water", "water supply", "water", "αñ¬αñ╛αñ¿αÑÇ", "αñ¬αÑÇαñ¿αÑç αñòαñ╛ αñ¬αñ╛αñ¿αÑÇ",
        "α«òα»üα«ƒα«┐α«¿α»Çα«░α»ì", "α«ñα«úα»ìα«úα»Çα«░α»ì", "α░ñα░╛α░ùα▒üα░¿α▒Çα░░α▒ü", "α░¿α▒Çα░░α▒ü", "αñ¬αñ┐αñúαÑìαñ»αñ╛αñÜαÑç αñ¬αñ╛αñúαÑÇ", "αñ¬αñ╛αñúαÑÇ",
    ],
    "roads": [
        "pothole", "road", "roads", "αñ╕αñíαñ╝αñò", "αñùαñíαÑìαñóαñ╛", "α«Üα«╛α«▓α»ê",
        "α░░α▒ïα░íα▒ìα░íα▒ü", "α░░α░╣α░ªα░╛α░░α░┐", "αñ░αñ╕αÑìαññαñ╛", "αñûαñíαÑìαñíαñ╛",
    ],
    "streetlights": [
        "streetlight", "street light", "αñ╕αÑìαñƒαÑìαñ░αÑÇαñƒ αñ▓αñ╛αñçαñƒ", "α«ñα»åα«░α»üα«╡α«┐α«│α«òα»ìα«òα»ü",
        "α░╡α▒Çα░ºα░┐ α░ªα▒Çα░¬α░é", "αñ¬αñÑαñªαñ┐αñ╡αñ╛", "αñ¬αñÑαñªαñ┐αñ╡αÑç",
    ],
    "sanitation": [
        "garbage", "sanitation", "waste", "drain", "αñòαñÜαñ░αñ╛", "αñ╕αñ½αñ╛αñê",
        "α«òα»üα«¬α»ìα«¬α»ê", "α«òα«┤α«┐α«╡α»üα«¿α»Çα«░α»ì", "α░Üα▒åα░ñα▒ìα░ñ", "α░¬α░╛α░░α░┐α░╢α▒üα░ºα▒ìα░»α░é", "αñ╕αÑìαñ╡αñÜαÑìαñ¢αññαñ╛", "αñùαñƒαñ╛αñ░",
    ],
    "electricity": [
        "electricity", "power cut", "power outage", "αñ¼αñ┐αñ£αñ▓αÑÇ",
        "α««α«┐α«⌐α»ìα«Üα«╛α«░α««α»ì", "α««α«┐α«⌐α»ìα«ñα«ƒα»ê", "α░╡α░┐α░ªα▒ìα░»α▒üα░ñα▒ì", "α░òα░░α▒åα░éα░ƒα▒ü", "αñ╡αÑÇαñ£", "αñ╡αÑÇαñ£αñ¬αÑüαñ░αñ╡αñáαñ╛",
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
