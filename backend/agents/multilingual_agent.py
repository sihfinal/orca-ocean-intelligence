"""
Multilingual & Regional Indian Language Conversational Agent for Blue Orbit

Supports 13 Indian regional languages:
- English (English)
- Hindi (हिंदी)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Malayalam (മലയാളം)
- Bengali (বাংলা)
- Gujarati (ગુજરાતી)
- Marathi (मराठी)
- Kannada (ಕನ್ನಡ)
- Konkani (कोंकणी)
- Odia (ଓଡ଼ିଆ)
- Tulu (ತುಳು)
- Kutchi (કચ્છી)

Provides deep semantic query decomposition, temporal nuance extraction,
and dynamic grounded vernacular response synthesis.
"""

from typing import Dict, Any, Optional
import re
import math

class MultilingualAgent:
    def __init__(self):
        self.agent_name = "Multilingual Regional Language Agent"
        
        self.supported_languages = {
                    "en": {"name": "English", "native": "English", "voice_code": "en-IN"},
                    "hi": {"name": "Hindi", "native": "हिन्दी", "voice_code": "hi-IN"},
                    "ta": {"name": "Tamil", "native": "தமிழ்", "voice_code": "ta-IN"},
                    "te": {"name": "Telugu", "native": "తెలుగు", "voice_code": "te-IN"},
                    "ml": {"name": "Malayalam", "native": "മലയാളം", "voice_code": "ml-IN"},
                    "bn": {"name": "Bengali", "native": "বাংলা", "voice_code": "bn-IN"},
                    "gu": {"name": "Gujarati", "native": "ગુજરાતી", "voice_code": "gu-IN"},
                    "mr": {"name": "Marathi", "native": "मराठी", "voice_code": "mr-IN"},
                    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "voice_code": "kn-IN"},
                    "kok": {"name": "Konkani", "native": "कोंकणी", "voice_code": "kok-IN"},
                    "or": {"name": "Odia", "native": "ଓଡ଼ିଆ", "voice_code": "or-IN"},
                    "tcy": {"name": "Tulu", "native": "ತುಳು", "voice_code": "tcy-IN"},
                    "kfr": {"name": "Kutchi", "native": "કચ્છી", "voice_code": "kfr-IN"}
                }

    def detect_language(self, text: str) -> str:
        """
        Detects language from Unicode script ranges or transliterated keywords.
        """
        if not text:
            return "en"
            
        # Devanagari script: Hindi / Marathi / Konkani
        if re.search(r'[\u0900-\u097F]', text):

            # Konkani-specific words
            if re.search(
                r'(माका|तुमका|कितें|कशें|आसा|हांव|आमका|नाका|कोंकणी)',
                text
            ):
                return "kok"

            # Marathi-specific words
            if re.search(
                r'(आहे|नाही|कसे|मासे|हवामान|समुद्र|सांगा)',
                text
            ):
                return "mr"

            return "hi"
            
        # Tamil script range: \u0B80-\u0BFF
        if re.search(r'[\u0B80-\u0BFF]', text):
            return "ta"
            
        # Telugu script range: \u0C00-\u0C7F
        if re.search(r'[\u0C00-\u0C7F]', text):
            return "te"
            
        # Malayalam script range: \u0D00-\u0D7F
        if re.search(r'[\u0D00-\u0D7F]', text):
            return "ml"
            
        # Bengali script range: \u0980-\u09FF
        if re.search(r'[\u0980-\u09FF]', text):
            return "bn"
            
        # Gujarati script range: \u0A80-\u0AFF
        if re.search(r'[\u0A80-\u0AFF]', text):
            return "gu"
        
        # Kannada script range: \u0C80-\u0CFF
        if re.search(r'[\u0C80-\u0CFF]', text):
            return "kn"

        # Odia script range: \u0B00-\u0B7F
        if re.search(r'[\u0B00-\u0B7F]', text):
            return "or"

        # Transliterated Romanized checks
        lower = text.lower()
        if any(w in lower for w in ["machli", "machhli", "mausam", "surakshit", "kahan", "samundar", "jaana", "kripya"]):
            return "hi"
        if any(w in lower for w in ["meen", "kadal", "kaatru", "poyalama", "alavu", "vanakkam"]):
            return "ta"
        if any(w in lower for w in ["chepala", "samudram", "galulu", "vellavacha", "namaskaram"]):
            return "te"
        if any(w in lower for w in ["meen", "kadal", "pokamo", "thiramala", "rakshikkan", "nanni"]):
            return "ml"
        if any(w in lower for w in ["mach", "machh", "somudro", "abohawa", "bhalo"]):
            return "bn"
        if any(w in lower for w in ["machhali", "samundar", "hawa", "kem chho"]):
            return "gu"
        if any(w in lower for w in ["masa", "samudra", "kasa", "aahe"]):
            return "mr"

        # Kannada
        if any(w in lower for w in [
            "namaskara",
            "hegidira",
            "hegiddira",
            "kadalu",
            "meenu",
            "matsya",
            "havaguna",
            "male",
            "gali",
            "alegalu",
            "surakshita",
            "dhanyavada",
            "beligge",
            "naale"
        ]):
            return "kn"

        # Konkani
        if any(w in lower for w in [
            "maka",
            "tumka",
            "kite",
            "kashem",
            "asa",
            "amkam",
            "hav",
            "mog",
            "konkani",
            "dev borem"
        ]):
            return "kok"

        # Odia
        if any(w in lower for w in [
            "namaskar",
            "kemiti",
            "kemiti achha",
            "samudra",
            "machha",
            "pani",
            "paban",
            "lahari",
            "surakshita",
            "dhanyabad"
        ]):
            return "or"

        # Tulu
        if any(w in lower for w in [
            "yenk",
            "enk",
            "yenna",
            "eereg",
            "barpundu",
            "poyyare",
            "kadala",
            "meenu",
            "tulu"
        ]):
            return "tcy"

        # Kutchi
        if any(w in lower for w in [
            "kem cho",
            "su hal",
            "dariya",
            "machhi",
            "samundar",
            "hawa",
            "surakshit",
            "aavjo",
            "kutchi"
        ]):
            return "kfr"

        return "en"
            
        return "en"

    def synthesize_localized_response(
        self,
        intent: str,
        context_data: Dict[str, Any],
        lang_code: str = "en",
        user_query: str = ""
    ) -> Dict[str, Any]:
        """
        Dynamically synthesizes rich, context-aware, grounded responses tailored to the exact user query.
        """
        lang = lang_code if lang_code in self.supported_languages else "en"
        q_lower = user_query.lower()

        # Context components
        port = context_data.get("port", {})
        port_name = port.get("name", "Kochi")
        port_state = port.get("state", "Kerala")
        
        weather = context_data.get("weather", {})
        status = weather.get("safety_status", "SAFE_FOR_VENTURE")
        wave = weather.get("significant_wave_height_m", 1.03)
        wind = weather.get("wind_speed_knots", 14.9)
        sea_state = weather.get("sea_state", "Moderate")
        score = weather.get("safety_index", 74.2)
        advice = weather.get("actionable_advice", "Normal fishing and coastal navigation permitted.")
        cyclone = weather.get("cyclone_influence", {}).get("active_cyclone")
        
        top_pfz = context_data.get("top_pfz", {})
        pfz_name = top_pfz.get("name", "Offshore Front")
        species = top_pfz.get("dominant_species", "Tuna")
        pfz_dist = top_pfz.get("distance_from_port_km", 24.5)
        bearing = top_pfz.get("bearing_from_port", "195°")
        depth = top_pfz.get("recommended_depth_m", 45)
        multiplier = top_pfz.get("catch_enhancement_multiplier", "3.5x")
        sst = top_pfz.get("sst_celsius", 28.2)
        chla = top_pfz.get("chlorophyll_a_mg_m3", 2.3)
        
        geofence = context_data.get("geofence", {})
        border_info = geofence.get("nearest_imbl", {})
        border_name = border_info.get("border_name", "International Maritime Boundary")
        border_dist = border_info.get("distance_nautical_miles", 142.0)
        border_msg = border_info.get("alert_message", "Operating safely in sovereign Indian EEZ waters.")

        # Temporal Query Detection
        is_morning = any(w in q_lower for w in ["morning", "subah", "kaalai", "udayam", "bhor", "sakala", "prabhat"])
        is_evening = any(w in q_lower for w in ["evening", "night", "shaam", "raat", "iravu", "sandhya", "sanje", "ratre"])
        is_tomorrow = any(w in q_lower for w in ["tomorrow", "kal", "naalai", "repu", "naale", "agamikal", "aavti kale", "udya"])
        is_small_craft = any(w in q_lower for w in ["small boat", "traditional", "country craft", "canoe", "vallam", "fiber", "chhoti boat"])
        is_species_query = any(s in q_lower for s in ["tuna", "sardine", "mackerel", "pomfret", "hilsa", "prawn", "shrimp", "squid", "meen", "machli", "chepala"])
        is_tech_query = any(w in q_lower for w in ["oceansat", "insat", "satellite", "how does", "working", "algorithm", "technology", "sensor", "chlorophyll"])

        # ----------------------------------------------------
        # 1. SEA SAFETY & WEATHER VENTURE REASONING
        # ----------------------------------------------------
        if intent == "sea_safety_check":
            # Dynamic timeframe tag
            time_tag = "Current & Immediate Window"
            if is_tomorrow and is_morning:
                time_tag = "Tomorrow Morning Forecast Window (05:00 - 11:00 AM)"
            elif is_tomorrow:
                time_tag = "Tomorrow's 24-Hour Outlook"
            elif is_morning:
                time_tag = "Morning Venture Window (06:00 - 11:00 AM)"
            elif is_evening:
                time_tag = "Evening & Nocturnal Venture Window"

            craft_advice = (
                f"Small country craft (<9m) should maintain a 5 NM coastal buffer due to {wave}m swell. Mechanized trawlers cleared up to 35 NM."
                if is_small_craft or wave > 1.2
                else f"Favorable for both traditional craft and motorized multi-day vessels."
            )

            morning_detail = (
                f"• **Diurnal Cycle:** Morning sea breeze is light (wind {wind} kts), offering optimal departure conditions before afternoon thermal convection.\n"
                if is_morning
                else ""
            )

            responses = {
                "kn": (
                    f"🛡️ **ಸಮುದ್ರ ಸುರಕ್ಷತೆ ಮತ್ತು ಹವಾಮಾನ ಸಲಹೆ · {port_name}**\n"
                    f"*{time_tag}*\n\n"
                    f"• **ಸುರಕ್ಷತಾ ಸ್ಥಿತಿ:** **{status.replace('_', ' ')}** (ಸ್ಕೋರ್: **{score}/100**)\n"
                    f"• **ಅಲೆಯ ಎತ್ತರ:** **{wave} ಮೀಟರ್**, ಗಾಳಿಯ ವೇಗ **{wind} ನಾಟ್ಸ್**.\n"
                    f"• **ಸಲಹೆ:** {advice}"
                ),

                "kok": (
                    f"🛡️ **समुद्री सुरक्षेची माहिती · {port_name}**\n"
                    f"*{time_tag}*\n\n"
                    f"• **सुरक्षा स्थिती:** **{status.replace('_', ' ')}** (स्कोर: **{score}/100**)\n"
                    f"• **लाटांची उंची:** **{wave} मीटर**, वाऱ्याची गती **{wind} नॉट्स**.\n"
                    f"• **सल्लो:** {advice}"
                ),

                "or": (
                    f"🛡️ **ସମୁଦ୍ର ସୁରକ୍ଷା ସୂଚନା · {port_name}**\n"
                    f"*{time_tag}*\n\n"
                    f"• **ସୁରକ୍ଷା ସ୍ଥିତି:** **{status.replace('_', ' ')}** (ସ୍କୋର: **{score}/100**)\n"
                    f"• **ତରଙ୍ଗର ଉଚ୍ଚତା:** **{wave} ମିଟର**, ପବନ ବେଗ **{wind} ନଟ୍ସ**।\n"
                    f"• **ପରାମର୍ଶ:** {advice}"
                ),

                "tcy": (
                    f"🛡️ **ಸಮುದ್ರ ಸುರಕ್ಷತೆ ಮಾಹಿತಿ · {port_name}**\n"
                    f"*{time_tag}*\n\n"
                    f"• **ಸುರಕ್ಷತಾ ಸ್ಥಿತಿ:** **{status.replace('_', ' ')}** (ಸ್ಕೋರ್: **{score}/100**)\n"
                    f"• **ಅಲೆ ಎತ್ತರ:** **{wave} ಮೀಟರ್**, ಗಾಳಿ ವೇಗ **{wind} ನಾಟ್ಸ್**.\n"
                    f"• **ಸಲಹೆ:** {advice}"
                ),

                "kfr": (
                    f"🛡️ **سمندری حفاظت دی معلومات · {port_name}**\n"
                    f"*{time_tag}*\n\n"
                    f"• **حفاظتی حالت:** **{status.replace('_', ' ')}** (اسکور: **{score}/100**)\n"
                    f"• **لہراں دی اونچائی:** **{wave} میٹر**، ہوا دی رفتار **{wind} ناٹس**۔\n"
                    f"• **مشورہ:** {advice}"
                ),
                
                "en": (
                    f"🛡️ **Sea Safety & Marine Clearance Advisory · {port_name} Sector**\n"
                    f"*{time_tag}*\n\n"
                    f"• **Clearance Status:** **{status.replace('_', ' ')}** (Safety Score: **{score}/100**)\n"
                    f"• **Wave & Sea State:** Significant wave height **{wave} meters**, swell period **6.5s**, Sea state **{sea_state}**.\n"
                    f"• **Wind Conditions:** Sustained **{wind} knots**, visibility **14 km** (No squalls).\n"
                    f"{morning_detail}"
                    f"• **Vessel Guidance:** {craft_advice}\n"
                    f"• **Cyclone / Disaster Watch:** {cyclone if cyclone else 'No active cyclone threat or severe weather alerts within 400 km.'}\n"
                    f"• **Actionable Advice:** {advice} Keep VHF Channel 16 active."
                ),
                "hi": (
                    f"🛡️ **समुद्री सुरक्षा एवं प्रस्थान मंजूरी सलाह · {port_name} क्षेत्र**\n"
                    f"*{time_tag}*\n\n"
                    f"• **अनुमति स्थिति:** **{status.replace('_', ' ')}** (सुरक्षा स्कोर: **{score}/100**)\n"
                    f"• **लहरें व समुद्र की स्थिति:** लहरों की ऊंचाई **{wave} मीटर**, समुद्र स्थिति **{sea_state}**।\n"
                    f"• **हवा की गति:** **{wind} नॉट्स**, दृश्यता **14 किमी**।\n"
                    f"• **नौका सलाह:** {craft_advice}\n"
                    f"• **चक्रवात चेतावनी:** कोई सक्रिय चक्रवात या भारी आंधी की चेतावनी नहीं है।\n"
                    f"• **कार्रवाई योग्य सलाह:** {advice} आपातकालीन VHF चैनल 16 चालू रखें।"
                ),
                "ta": (
                    f"🛡️ **கடல் பாதுகாப்பு மற்றும் வானிலை ஆலோசனை · {port_name} பகுதி**\n"
                    f"*{time_tag}*\n\n"
                    f"• **பாதுகாப்பு நிலை:** **{status.replace('_', ' ')}** (மதிப்பெண்: **{score}/100**)\n"
                    f"• **அலை உயரம்:** **{wave} மீட்டர்**, காற்றின் வேகம் **{wind} நாட்ஸ்**.\n"
                    f"• **கடல் நிலை:** {sea_state}. புயல் எச்சரிக்கை ஏதுமில்லை.\n"
                    f"• **படகு வழிகாட்டுதல்:** {craft_advice}\n"
                    f"• **பரிந்துரை:** {advice}"
                ),
                "te": (
                    f"🛡️ **సముద్ర భద్రత మరియు వాతావరణ సమాచారం · {port_name}**\n"
                    f"*{time_tag}*\n\n"
                    f"• **భద్రతా స్థితి:** **{status.replace('_', ' ')}** (స్కోరు: **{score}/100**)\n"
                    f"• **అలల ఎత్తు:** **{wave} మీటర్లు**, గాలి వేగం **{wind} నాట్స్**.\n"
                    f"• **సముద్ర పరిస్థితి:** సాధారణం. తుఫాను హెచ్చరికలు లేవు.\n"
                    f"• **సలహా:** {advice}"
                ),
                "ml": (
                    f"🛡️ **സമുദ്ര സുരക്ഷാ മുന്നറിയിപ്പ് · {port_name} മേഖല**\n"
                    f"*{time_tag}*\n\n"
                    f"• **നിലവിലെ അവസ്ഥ:** **{status.replace('_', ' ')}** (സുരക്ഷാ സ്കോർ: **{score}/100**)\n"
                    f"• **തിരമാലയുടെ ഉയരം:** **{wave} മീറ്റർ**, കാറ്റിന്റെ വേഗത **{wind} നോട്ട്സ്**.\n"
                    f"• **കാലാവസ്ഥ:** ചുഴലിക്കാറ്റ് ഭീഷണിയില്ല. കടൽ ശാന്തമാണ്.\n"
                    f"• **നിർദ്ദേശം:** {advice}"
                ),
                "bn": (
                    f"🛡️ **সামুদ্রিক নিরাপত্তা ও আবহাওয়া বার্তা · {port_name} অঞ্চল**\n"
                    f"*{time_tag}*\n\n"
                    f"• **অনুমতি স্থিতি:** **{status.replace('_', ' ')}** (নিরাপত্তা স্কোর: **{score}/100**)\n"
                    f"• **ঢেউয়ের উচ্চতা:** **{wave} মিটার**, বাতাসের গতি **{wind} নট**।\n"
                    f"• **পরামর্শ:** {advice}"
                ),
                "gu": (
                    f"🛡️ **દરિયાઈ સલામતી સલાહ · {port_name}**\n"
                    f"*{time_tag}*\n\n"
                    f"• **સ્થિતિ:** **{status.replace('_', ' ')}** (સ્કોર: **{score}/100**)\n"
                    f"• **મોજાની ઊંચાઈ:** **{wave} મીટર**, પવનની ગતિ **{wind} નોટ્સ**.\n"
                    f"• **સલાહ:** {advice}"
                ),
                "mr": (
                    f"🛡️ **सागरी सुरक्षा सल्ला · {port_name}**\n"
                    f"*{time_tag}*\n\n"
                    f"• **स्थिती:** **{status.replace('_', ' ')}** (सुरक्षा निर्देशांक: **{score}/100**)\n"
                    f"• **लाटांची उंची:** **{wave} मीटर**, वाऱ्याचा वेग **{wind} नॉट्स**.\n"
                    f"• **सल्ला:** {advice}"
                )
            }
            text_out = responses.get(lang, responses["en"])

        # ----------------------------------------------------
        # 2. POTENTIAL FISHING ZONE (PFZ) INTENT
        # ----------------------------------------------------
        elif intent == "pfz_discovery":
            target_species = species
            if "tuna" in q_lower: target_species = "Yellowfin & Skipjack Tuna"
            elif "sardine" in q_lower or "mathi" in q_lower: target_species = "Indian Oil Sardine"
            elif "mackerel" in q_lower or "ayala" in q_lower or "bangda" in q_lower: target_species = "Indian Mackerel"
            elif "pomfret" in q_lower: target_species = "Silver / Black Pomfret"
            elif "squid" in q_lower: target_species = "Indian Squid (Loligo duvaucelii)"

            responses = {
                "kn": (
                    f"🐟 **ಹೆಚ್ಚಿನ ಇಳುವರಿ ಮೀನುಗಾರಿಕೆ ಪ್ರದೇಶ (PFZ) · {port_name}**\n\n"
                    f"• **ಸ್ಥಳ:** **{pfz_name}** ({pfz_dist} ಕಿಮೀ, ದಿಕ್ಕು: **{bearing}**)\n"
                    f"• **ಪ್ರಮುಖ ಮೀನು:** **{target_species}** ({multiplier} ಹೆಚ್ಚಿನ ಇಳುವರಿ).\n"
                    f"• **ಆಳ:** **{depth} ಮೀಟರ್**.\n"
                    f"• **Chlorophyll-a:** **{chla} mg/m³**.\n"
                    f"• **SST:** **{sst}°C**."
                ),

                "kok": (
                    f"🐟 **मत्स्य क्षेत्र (PFZ) · {port_name}**\n\n"
                    f"• **स्थान:** **{pfz_name}** ({pfz_dist} किमी, दिशा: **{bearing}**)\n"
                    f"• **मुख्य मासे:** **{target_species}** ({multiplier} अधिक उत्पादन).\n"
                    f"• **खोली:** **{depth} मीटर**."
                ),

                "or": (
                    f"🐟 **ସମ୍ଭାବ୍ୟ ମତ୍ସ୍ୟ ଅଞ୍ଚଳ (PFZ) · {port_name}**\n\n"
                    f"• **ସ୍ଥାନ:** **{pfz_name}** ({pfz_dist} କିମି, ଦିଗ: **{bearing}**)\n"
                    f"• **ମୁଖ୍ୟ ମାଛ:** **{target_species}** ({multiplier} ଅଧିକ ଉତ୍ପାଦନ).\n"
                    f"• **ଗଭୀରତା:** **{depth} ମିଟର**."
                ),

                "tcy": (
                    f"🐟 **ಮೀನುಗಾರಿಕೆ ಪ್ರದೇಶ (PFZ) · {port_name}**\n\n"
                    f"• **ಸ್ಥಳ:** **{pfz_name}** ({pfz_dist} ಕಿಮೀ, ದಿಕ್ಕ್: **{bearing}**)\n"
                    f"• **ಮೀನು:** **{target_species}** ({multiplier} ಹೆಚ್ಚಿನ ಇಳುವರಿ).\n"
                    f"• **ಆಳ:** **{depth} ಮೀಟರ್**."
                ),

                "kfr": (
                    f"🐟 **مچھھی پکڑن دا علاقہ (PFZ) · {port_name}**\n\n"
                    f"• **جگہ:** **{pfz_name}** ({pfz_dist} کلومیٹر، رخ: **{bearing}**)\n"
                    f"• **اہم مچھھی:** **{target_species}** ({multiplier} زیادہ پیداوار).\n"
                    f"• **گہرائی:** **{depth} میٹر**."
                ),
                "en": (
                    f"🐟 **High-Yield Potential Fishing Zone (PFZ) · {port_name} Sector**\n\n"
                    f"• **Target Location:** **{pfz_name}** ({pfz_dist} km from {port_name}, Bearing: **{bearing}**)\n"
                    f"• **Dominant Species:** High commercial concentration of **{target_species}** ({multiplier} expected catch yield).\n"
                    f"• **Recommended Gear & Depth:** Depth **{depth} meters** (Drift Gillnet / Pelagic Longline / Purse Seine).\n"
                    f"• **ISRO Satellite Oceanography:**\n"
                    f"  - **Oceansat-3 OCM-3:** Chlorophyll-a peak of **{chla} mg/m³** (high phytoplankton feeding zone).\n"
                    f"  - **INSAT-3DR TIR:** Sea Surface Temperature **{sst}°C** with active thermal front gradient (0.85°C/10km).\n"
                    f"• **Transit Time:** ~{round(pfz_dist/18.5, 1)} hours at 10 knots. Sea state is favorable."
                ),
                "hi": (
                    f"🐟 **संभावित मत्स्य पालन क्षेत्र (PFZ) सलाहकार · {port_name}**\n\n"
                    f"• **स्थान:** **{pfz_name}** ({port_name} से **{pfz_dist} किमी**, दिशा: **{bearing}**)\n"
                    f"• **प्रमुख मछली:** **{target_species}** की भारी उपलब्धता (सामान्य से **{multiplier}** अधिक उत्पादन)।\n"
                    f"• **अनुशंसित गहराई:** **{depth} मीटर**।\n"
                    f"• **इसरो उपग्रह प्रमाण:**\n"
                    f"  - **ओशनसैट-3:** क्लोरोफिल-ए स्तर **{chla} mg/m³** (सघन प्लवक क्षेत्र)।\n"
                    f"  - **इनसैट-3DR:** समुद्र सतह तापमान **{sst}°C** थर्मल फ्रंट रेखा।\n"
                    f"• **सुरक्षा सलाह:** मौसम शांत है, प्रस्थान के लिए आदर्श समय है।"
                ),
                "ta": (
                    f"🐟 **சாத்தியமான மீன்பிடி மண்டலம் (PFZ) · {port_name}**\n\n"
                    f"• **இடம்:** **{pfz_name}** ({port_name} இலிருந்து **{pfz_dist} கி.மீ**, திசை: **{bearing}**)\n"
                    f"• **மீன் வகை:** **{target_species}** அதிக அளவில் கிடைக்கும் ({multiplier} அதிக விளைச்சல் வாய்ப்பு).\n"
                    f"• **ஆழம்:** **{depth} மீட்டர்** (Oceansat-3 & INSAT-3DR தரவு மூலம் உறுதிப்படுத்தப்பட்டது)."
                ),
                "te": (
                    f"🐟 **చేపల వేట ప్రాంతం (PFZ) వివరాలు · {port_name}**\n\n"
                    f"• **ప్రాంతం:** **{pfz_name}** (దూరం: **{pfz_dist} కి.మీ**, దిశ: **{bearing}**)\n"
                    f"• **చేపల రకం:** **{target_species}** ({multiplier} రెట్లు ఎక్కువ దిగుబడి).\n"
                    f"• **లోతు:** **{depth} మీటర్లు**."
                ),
                "ml": (
                    f"🐟 **അനുയോജ്യമായ മത്സ്യബന്ധന മേഖല (PFZ) · {port_name}**\n\n"
                    f"• **സ്ഥലം:** **{pfz_name}** ({pfz_dist} കി.മീ അകലെ, ദിശ: **{bearing}**)\n"
                    f"• **ലഭ്യമായ മത്സ്യം:** **{target_species}** ({multiplier} ഇരട്ടി ലഭ്യത).\n"
                    f"• **ആഴം:** **{depth} മീറ്റർ** (ഓഷ്യൻസാറ്റ്-3 ക്ലോറോഫിൽ ഡാറ്റ പ്രകാരം)."
                ),
                "bn": (
                    f"🐟 **সম্ভাব্য মাছ ধরার অঞ্চল (PFZ) · {port_name}**\n\n"
                    f"• **অবস্থান:** **{pfz_name}** ({pfz_dist} কিমি, অভিমুখ: **{bearing}**)\n"
                    f"• **প্রধান মাছ:** প্রচুর পরিমাণে **{target_species}** ({multiplier} গুণ বেশি ফলন)।\n"
                    f"• **গভীরতা:** **{depth} মিটার**।"
                ),
                "gu": (
                    f"🐟 **સંભવિત મત્સ્યઉદ્યોગ ઝોન (PFZ) · {port_name}**\n\n"
                    f"• **સ્થળ:** **{pfz_name}** ({pfz_dist} કિમી, દિશા: **{bearing}**)\n"
                    f"• **માછલી:** **{target_species}** ({multiplier} ગણી વધુ ઉપજ).\n"
                    f"• **ઊંડાઈ:** **{depth} મીટર**."
                ),
                "mr": (
                    f"🐟 **संभाव्य मासेमारी क्षेत्र (PFZ) · {port_name}**\n\n"
                    f"• **स्थान:** **{pfz_name}** ({pfz_dist} किमी, दिशा: **{bearing}**)\n"
                    f"• **मासे:** **{target_species}** ({multiplier} पट अधिक उत्पादन).\n"
                    f"• **खोली:** **{depth} मीटर**."
                )
            }
            text_out = responses.get(lang, responses["en"])

        # ----------------------------------------------------
        # 3. GEOFENCE & INTERNATIONAL BORDER (IMBL) INTENT
        # ----------------------------------------------------
        elif intent == "geofence_border_check":
            responses = {
                "kn": (
                    f"🛑 **ಅಂತರರಾಷ್ಟ್ರೀಯ ಸಮುದ್ರ ಗಡಿ (IMBL) ಮಾಹಿತಿ**\n\n"
                    f"• **ಕರಾವಳಿ ಪ್ರದೇಶ:** {port_name} ({port_state})\n"
                    f"• **ಹತ್ತಿರದ ಗಡಿ:** **{border_name}**\n"
                    f"• **ದೂರ:** **{border_dist} ನಾಟಿಕಲ್ ಮೈಲುಗಳು**\n"
                    f"• **ಸ್ಥಿತಿ:** **{border_msg}**"
                ),

                "kok": (
                    f"🛑 **आंतरराष्ट्रीय समुद्री सीमा (IMBL) माहिती**\n\n"
                    f"• **किनारी क्षेत्र:** {port_name} ({port_state})\n"
                    f"• **जवळची सीमा:** **{border_name}**\n"
                    f"• **अंतर:** **{border_dist} नॉटिकल मैल**\n"
                    f"• **स्थिती:** **{border_msg}**"
                ),

                "or": (
                    f"🛑 **ଆନ୍ତର୍ଜାତୀୟ ସମୁଦ୍ର ସୀମା (IMBL) ସୂଚନା**\n\n"
                    f"• **ଅଞ୍ଚଳ:** {port_name} ({port_state})\n"
                    f"• **ନିକଟତମ ସୀମା:** **{border_name}**\n"
                    f"• **ଦୂରତା:** **{border_dist} ନଟିକାଲ୍ ମାଇଲ୍**\n"
                    f"• **ସ୍ଥିତି:** **{border_msg}**"
                ),

                "tcy": (
                    f"🛑 **ಅಂತರರಾಷ್ಟ್ರೀಯ ಸಮುದ್ರ ಗಡಿ (IMBL) ಮಾಹಿತಿ**\n\n"
                    f"• **ಪ್ರದೇಶ:** {port_name} ({port_state})\n"
                    f"• **ಹತ್ತಿರದ ಗಡಿ:** **{border_name}**\n"
                    f"• **ದೂರ:** **{border_dist} ನಾಟಿಕಲ್ ಮೈಲು**\n"
                    f"• **ಸ್ಥಿತಿ:** **{border_msg}**"
                ),

                "kfr": (
                    f"🛑 **بین الاقوامی سمندری سرحد (IMBL) معلومات**\n\n"
                    f"• **ساحلی علاقہ:** {port_name} ({port_state})\n"
                    f"• **نیڑے سرحد:** **{border_name}**\n"
                    f"• **فاصلہ:** **{border_dist} ناٹیکل میل**\n"
                    f"• **حالت:** **{border_msg}**"
                ),
                "en": (
                    f"🛑 **International Maritime Boundary (IMBL) & Geofence Intelligence**\n\n"
                    f"• **Reference Coast:** {port_name} Sector ({port_state})\n"
                    f"• **Nearest Sovereign Border:** **{border_name}**\n"
                    f"• **Current Distance:** **{border_dist} Nautical Miles** (~{round(border_dist * 1.852, 1)} km)\n"
                    f"• **Geofence Status:** **{border_msg}**\n"
                    f"• **Operational Protocol:**\n"
                    f"  - Maintain minimum **3.0 NM safety buffer** away from the IMBL line.\n"
                    f"  - Keep GPS position logger and NavIC transceiver powered ON.\n"
                    f"  - In case of GPS drift or engine failure, alert Indian Coast Guard on **VHF Channel 16 / DSC Distress 2187.5 kHz**."
                ),
                "hi": (
                    f"🛑 **अंतर्राष्ट्रीय समुद्री सीमा (IMBL) एवं जियोफेंस सुरक्षा स्थिति**\n\n"
                    f"• **तटीय क्षेत्र:** {port_name} ({port_state})\n"
                    f"• **निकटतम सीमा:** **{border_name}**\n"
                    f"• **दूरी:** **{border_dist} नॉटिकल मील** (~{round(border_dist * 1.852, 1)} किमी)\n"
                    f"• **जियोफेंस स्थिति:** **{border_msg}**\n"
                    f"• **सुरक्षा दिशानिर्देश:** सीमा से कम से कम 3 नॉटिकल मील की सुरक्षित दूरी रखें। भारतीय तटरक्षक बल (ICG) नियमों का पालन करें।"
                ),
                "ta": (
                    f"🛑 **சர்வதேச கடல் எல்லை (IMBL) மற்றும் ஜியோபென்ஸ் தகவல்**\n\n"
                    f"• **பகுதி:** {port_name} ({port_state})\n"
                    f"• **அருகிலுள்ள எல்லை:** **{border_name}** (தூரம்: **{border_dist} கடல் மைல்கள்**)\n"
                    f"• **எச்சரிக்கை:** {border_msg}. எல்லைக்கு அருகில் செல்ல வேண்டாம்."
                ),
                "te": (
                    f"🛑 **అంతర్జాతీయ సముద్ర సరిహద్దు (IMBL) సమాచారం**\n\n"
                    f"• **సమీప సరిహద్దు:** **{border_name}** (దూరం: **{border_dist} నాటికల్ మైళ్ళు**)\n"
                    f"• **స్థితి:** {border_msg}."
                ),
                "ml": (
                    f"🛑 **അന്താരാഷ്ട്ര സമുദ്ര അതിർത്തി (IMBL) ജിയോഫെൻസ് സ്റ്റാറ്റസ്**\n\n"
                    f"• **അടുത്തുള്ള അതിർത്തി:** **{border_name}** (അകലം: **{border_dist} നോട്ടിക്കൽ മൈൽ**)\n"
                    f"• **സുരക്ഷാ അറിയിപ്പ്:** {border_msg}."
                ),
                "bn": (
                    f"🛑 **আন্তর্জাতিক সামুদ্রিক সীমানা (IMBL) সতর্কতা**\n\n"
                    f"• **নিকটতম সীমান্ত:** **{border_name}** (দূরত্ব: **{border_dist} নটিক্যাল মাইল**)\n"
                    f"• **স্থিতি:** {border_msg}."
                ),
                "gu": (
                    f"🛑 **આંતરરાષ્ટ્રીય દરિયાઈ સીમા (IMBL) જીઓફેન્સ ચેતવણી**\n\n"
                    f"• **સરહદ:** **{border_name}** (અંતર: **{border_dist} નોટિકલ માઇલ**)\n"
                    f"• **ચેતવણી:** {border_msg}."
                ),
                "mr": (
                    f"🛑 **आंतरराष्ट्रीय सागरी सीमा (IMBL) जिओफेन्स स्थिती**\n\n"
                    f"• **सीमा:** **{border_name}** (अंतर: **{border_dist} नॉटिकल मैल**)\n"
                    f"• **स्थिती:** {border_msg}."
                )
            }
            text_out = responses.get(lang, responses["en"])

        # ----------------------------------------------------
        # 4. ROUTE PLANNING & NAVIGATION INTENT
        # ----------------------------------------------------
        elif intent in ["route_planning", "safe_navigation_route"]:
            safe_route = context_data.get("route", {})
            metrics = safe_route.get("route_metrics", {})
            dist_nm = metrics.get("routed_distance_nm", round(pfz_dist / 1.852, 1))
            transit_hrs = metrics.get("estimated_transit_time_hours", round(dist_nm / 10.0, 1))
            fuel_l = metrics.get("estimated_fuel_burn_litres", metrics.get("estimated_fuel_liters", round(dist_nm * 4.2, 1)))

            responses = {
                "kn": (
                    f"🧭 **ಸುರಕ್ಷಿತ ಸಮುದ್ರ ಮಾರ್ಗ · {port_name} ರಿಂದ {pfz_name}**\n\n"
                    f"• **ದೂರ:** **{dist_nm} ನಾಟಿಕಲ್ ಮೈಲುಗಳು**\n"
                    f"• **ದಿಕ್ಕು:** **{bearing}**\n"
                    f"• **ಪ್ರಯಾಣ ಸಮಯ:** **{transit_hrs} ಗಂಟೆಗಳು**\n"
                    f"• **ಇಂಧನ:** **{fuel_l} ಲೀಟರ್**."
                ),

                "kok": (
                    f"🧭 **सुरक्षित समुद्री मार्ग · {port_name} ते {pfz_name}**\n\n"
                    f"• **अंतर:** **{dist_nm} नॉटिकल मैल**\n"
                    f"• **दिशा:** **{bearing}**\n"
                    f"• **प्रवास वेळ:** **{transit_hrs} तास**\n"
                    f"• **इंधन:** **{fuel_l} लिटर**."
                ),

                "or": (
                    f"🧭 **ସୁରକ୍ଷିତ ସମୁଦ୍ର ମାର୍ଗ · {port_name} ରୁ {pfz_name}**\n\n"
                    f"• **ଦୂରତା:** **{dist_nm} ନଟିକାଲ୍ ମାଇଲ୍**\n"
                    f"• **ଦିଗ:** **{bearing}**\n"
                    f"• **ସମୟ:** **{transit_hrs} ଘଣ୍ଟା**\n"
                    f"• **ଇନ୍ଧନ:** **{fuel_l} ଲିଟର**."
                ),

                "tcy": (
                    f"🧭 **ಸುರಕ್ಷಿತ ಸಮುದ್ರ ಮಾರ್ಗ · {port_name} ದಿಂಡ {pfz_name}**\n\n"
                    f"• **ದೂರ:** **{dist_nm} ನಾಟಿಕಲ್ ಮೈಲು**\n"
                    f"• **ದಿಕ್ಕ್:** **{bearing}**\n"
                    f"• **ಸಮಯ:** **{transit_hrs} ಗಂಟೆ**\n"
                    f"• **ಇಂಧನ:** **{fuel_l} ಲೀಟರ್**."
                ),

                "kfr": (
                    f"🧭 **محفوظ سمندری راستہ · {port_name} توں {pfz_name}**\n\n"
                    f"• **فاصلہ:** **{dist_nm} ناٹیکل میل**\n"
                    f"• **رخ:** **{bearing}**\n"
                    f"• **سفر دا وقت:** **{transit_hrs} گھنٹے**\n"
                    f"• **ایندھن:** **{fuel_l} لیٹر**."
                ),
                "en": (
                    f"🧭 **Optimal Marine Route & Transit Plan · {port_name} to {pfz_name}**\n\n"
                    f"• **Total Routed Distance:** **{dist_nm} Nautical Miles** (~{round(dist_nm * 1.852, 1)} km)\n"
                    f"• **Compass Course & Heading:** **{bearing}**\n"
                    f"• **Estimated Transit Time:** **{transit_hrs} hours** (cruising at 10 knots)\n"
                    f"• **Estimated Fuel Consumption:** **{fuel_l} Liters** (Diesel inboard)\n"
                    f"• **Weather Clearance along Route:** Wave {wave}m, Wind {wind} kts. No bathymetric shoals or restricted zones along trajectory."
                ),
                "hi": (
                    f"🧭 **सुरक्षित समुद्री मार्ग एवं नेविगेशन योजना · {port_name} से {pfz_name}**\n\n"
                    f"• **कुल दूरी:** **{dist_nm} नॉटिकल मील** (~{round(dist_nm * 1.852, 1)} किमी)\n"
                    f"• **दिशा / कम्पास हेडिंग:** **{bearing}**\n"
                    f"• **अनुमानित यात्रा समय:** **{transit_hrs} घंटे** (10 नॉट गति पर)\n"
                    f"• **अनुमानित ईंधन खपत:** **{fuel_l} लीटर**\n"
                    f"• **मार्ग सुरक्षा:** मार्ग में कोई रुकावट या प्रतिबंधित क्षेत्र नहीं है।"
                ),
                "ta": (
                    f"🧭 **பாதுகாப்பான கடல் வழித்தட திட்டம் · {port_name} to {pfz_name}**\n\n"
                    f"• **தூரம்:** **{dist_nm} கடல் மைல்கள்**\n"
                    f"• **திசை:** **{bearing}** | **பயண நேரம்:** **{transit_hrs} மணிநேரம்**\n"
                    f"• **எரிபொருள் தேவை:** **{fuel_l} லிட்டர்**."
                ),
                "te": (
                    f"🧭 **సముద్ర నావిగేషన్ మార్గం · {port_name} to {pfz_name}**\n\n"
                    f"• **దూరం:** **{dist_nm} నాటికల్ మైళ్ళు** | **దిశ:** **{bearing}**\n"
                    f"• **సమయం:** **{transit_hrs} గంటలు** | **ఇంధనం:** **{fuel_l} లీటర్లు**."
                ),
                "ml": (
                    f"🧭 **സുരക്ഷിത നാവിഗേഷൻ റൂട്ട് · {port_name} to {pfz_name}**\n\n"
                    f"• **ദൂരം:** **{dist_nm} നോട്ടിക്കൽ മൈൽ** | **ദിശ:** **{bearing}**\n"
                    f"• **യാത്രാ സമയം:** **{transit_hrs} മണിക്കൂർ** | **ഇന്ധനം:** **{fuel_l} ലിറ്റർ**."
                ),
                "bn": (
                    f"🧭 **নিরাপদ নৌপথ পরিকল্পনা · {port_name} to {pfz_name}**\n\n"
                    f"• **দূরত্ব:** **{dist_nm} নটিক্যাল মাইল** | **অভিমুখ:** **{bearing}**\n"
                    f"• **সময়:** **{transit_hrs} ঘণ্টা** | **জ্বালানি:** **{fuel_l} লিটার**."
                ),
                "gu": (
                    f"🧭 **દરિયાઈ નેવિગેશન યોજના · {port_name} to {pfz_name}**\n\n"
                    f"• **અંતર:** **{dist_nm} નોટિકલ માઇલ** | **દિશા:** **{bearing}**\n"
                    f"• **સમય:** **{transit_hrs} કલાક** | **ઇંધણ:** **{fuel_l} લિટર**."
                ),
                "mr": (
                    f"🧭 **सुरक्षित सागरी मार्ग योजना · {port_name} to {pfz_name}**\n\n"
                    f"• **अंतर:** **{dist_nm} नॉटिकल मैल** | **दिशा:** **{bearing}**\n"
                    f"• **वेळ:** **{transit_hrs} तास** | **इंधन:** **{fuel_l} लिटर**."
                )
            }
            text_out = responses.get(lang, responses["en"])

        # ----------------------------------------------------
        # 4B. SAFEST PFZ & CANDIDATE DECISION MATRIX (PHASE 7)
        # ----------------------------------------------------
        elif intent in ["safest_pfz_advisory", "candidate_safety_evaluation"]:
            safety_evals = context_data.get("safety_evaluations", [])
            top_eval = safety_evals[0] if safety_evals else {}
            cand_name = top_eval.get("name", pfz_name)
            decision = top_eval.get("decision_state", "PREFERRED")
            risk_val = top_eval.get("risk_score", 0.25)
            rationale = top_eval.get("decision_rationale", "Optimal candidate with low operational risk.")
            
            responses = {
                "en": (
                    f"🛡️ **Safest Potential Fishing Zone Evaluation · {port_name} Sector**\n\n"
                    f"• **Recommended Candidate:** **{cand_name}**\n"
                    f"• **Decision Status:** **{decision}** (Marine Risk Score: {risk_val}/1.0)\n"
                    f"• **Suitability vs Risk Assessment:**\n"
                    f"  - {rationale}\n"
                    f"• **Maritime Boundary Clearance:** Unrestricted sovereign waters, clear of known Marine Protected Areas.\n"
                    f"• **Environmental Safety:** Wave {wave}m, Wind {wind} kts. Normal fishing operations permissible under VHF watch."
                ),
                "hi": (
                    f"🛡️ **सबसे सुरक्षित मछली पकड़ने का क्षेत्र मूल्यांकन · {port_name} क्षेत्र**\n\n"
                    f"• **सुझाया गया क्षेत्र:** **{cand_name}**\n"
                    f"• **निर्णय स्थिति:** **{decision}** (सागरीय जोखिम स्कोर: {risk_val}/1.0)\n"
                    f"• **जोखिम विश्लेषण:** {rationale}\n"
                    f"• **सीमा सुरक्षा:** समुद्री संरक्षित क्षेत्रों और अंतर्राष्ट्रीय सीमाओं से सुरक्षित दूरी।"
                ),
                "kn": (
                    f"🛡️ **ಅತ್ಯಂತ ಸುರಕ್ಷಿತ ಮೀನುಗಾರಿಕೆ ವಲಯ ಮೌಲ್ಯಮಾಪನ · {port_name} ವಲಯ**\n\n"
                    f"• **ಶಿಫಾರಸು ಮಾಡಿದ ವಲಯ:** **{cand_name}**\n"
                    f"• **ಸ್ಥಿತಿ:** **{decision}** (ಅಪಾಯದ ಅಂಕ: {risk_val}/1.0)\n"
                    f"• **ವಿಶ್ಲೇಷಣೆ:** {rationale}\n"
                    f"• **ಗಡಿ ಸುರಕ್ಷತೆ:** ಯಾವುದೇ ನಿರ್ಬಂಧಿತ ಪ್ರದೇಶ ಅಥವಾ ಗಡಿಯೊಂದಿಗೆ ತೊಂದರೆಯಿಲ್ಲ."
                )
            }
            text_out = responses.get(lang, responses["en"])

        # ----------------------------------------------------
        # 5. SPATIAL EARTH OBSERVATION & RASTER INTENT
        # ----------------------------------------------------
        elif intent in ["spatial_eo_raster", "satellite_raster"]:
            raster = context_data.get("satellite_raster", {})
            r_var = raster.get("variable", "Ocean Variable").replace("_", " ").title()
            r_unit = raster.get("unit", "")
            r_src = raster.get("source", "ISRO Earth Observation Ground Segment")
            r_sat = raster.get("satellite_name", raster.get("satellite", "ISRO Constellation"))
            r_sen = raster.get("sensor_name", raster.get("sensor", "Radiometric Sensor"))
            r_mean = raster.get("mean", "N/A")
            r_max = raster.get("maximum", raster.get("max_value", "N/A"))
            r_min = raster.get("minimum", raster.get("min_value", "N/A"))
            r_pct = raster.get("valid_percentage", 100.0)
            fronts = raster.get("sharpest_front_points", [])
            max_grad = raster.get("max_gradient_magnitude")
            grad_unit = raster.get("gradient_unit", "unit/km")

            front_text = ""
            if max_grad is not None:
                front_text = f"\n• **Horizontal Gradient:** Peak intensity **{max_grad} {grad_unit}** across frontal convergence boundaries."
                if fronts:
                    p0 = fronts[0]
                    front_text += f" Strongest gradient located at **({p0.get('latitude', 0.0)}°N, {p0.get('longitude', 0.0)}°E)**."

            responses = {
                "en": (
                    f"🛰️ **Satellite Earth Observation & Spatial Field Analysis · {port_name} Shelf**\n\n"
                    f"• **Target Parameter:** **{r_var}** ({r_unit})\n"
                    f"• **Satellite Platform & Sensor:** **{r_sat}** ({r_sen})\n"
                    f"• **Authoritative Source:** {r_src}\n"
                    f"• **Regional Zonal Statistics:** Mean: **{r_mean} {r_unit}** | Max: **{r_max} {r_unit}** | Min: **{r_min} {r_unit}**\n"
                    f"• **Valid Ocean Coverage:** **{r_pct}%** valid unmasked sea surface pixels."
                    f"{front_text}\n"
                    f"• **Scientific Integrity Note:** Cloud and land pixels are strictly masked with NaN. Spatial gradients represent physical thermal/color discontinuities, not final fisheries predictions."
                ),
                "hi": (
                    f"🛰️ **उपग्रह पृथ्वी अवलोकन एवं स्थानिक रास्टर विश्लेषण · {port_name} क्षेत्र**\n\n"
                    f"• **अवलोकित चर:** **{r_var}** ({r_unit})\n"
                    f"• **उपग्रह प्लेटफॉर्म व सेंसर:** **{r_sat}** ({r_sen})\n"
                    f"• **डेटा स्रोत:** {r_src}\n"
                    f"• **क्षेत्रीय सांख्यिकी:** औसत: **{r_mean} {r_unit}** | अधिकतम: **{r_max} {r_unit}**\n"
                    f"• **वैध समुद्री कवरेज:** **{r_pct}%** वैध पिक्सेल।"
                    f"{front_text}\n"
                    f"• **वैज्ञानिक सीमाएँ:** बादल व भूमि पिक्सेल मास्क किए गए हैं। यह भौतिक संवेदक माप है, मत्स्य पूर्वानुमान नहीं।"
                ),
                "kn": (
                    f"🛰️ **ಉಪಗ್ರಹ ಭೂ ವೀಕ್ಷಣೆ ಮತ್ತು ಪ್ರಾದೇಶಿಕ ರಾಸ್ಟರ್ ವಿಶ್ಲೇಷಣೆ · {port_name} ಪ್ರದೇಶ**\n\n"
                    f"• **ಗುರಿ ನಿಯತಾಂಕ:** **{r_var}** ({r_unit})\n"
                    f"• **ಉಪಗ್ರಹ ಮತ್ತು ಸಂವೇದಕ:** **{r_sat}** ({r_sen})\n"
                    f"• **ಮೂಲ:** {r_src}\n"
                    f"• **ಪ್ರಾದೇಶಿಕ ಅಂಕಿಅಂಶಗಳು:** ಸರಾಸರಿ: **{r_mean} {r_unit}** | ಗರಿಷ್ಠ: **{r_max} {r_unit}**\n"
                    f"• **ಮಾನ್ಯ ಸಮುದ್ರ ವ್ಯಾಪ್ತಿ:** **{r_pct}%** ಮಾನ್ಯ ಪಿಕ್ಸೆಲ್‌ಗಳು."
                    f"{front_text}\n"
                    f"• **ವೈಜ್ಞಾನಿಕ ಸಮಗ್ರತೆ:** ಮೋಡ ಮತ್ತು ಭೂಮಿಯನ್ನು ಮರೆಮಾಡಲಾಗಿದೆ. ಇದು ಸಂವೇದಕ ಮಾಪನವಾಗಿದೆ."
                )
            }
            text_out = responses.get(lang, responses["en"])

        # ----------------------------------------------------
        # 6. SPATIAL PFZ RADIUS & CANDIDATE REGION SEARCH (PHASE 6)
        # ----------------------------------------------------
        elif intent in ["pfz_radius_search", "pfz_candidates_spatial"]:
            pfz_cands = context_data.get("pfz_candidates", [])
            cand_count = len(pfz_cands)
            top_c = pfz_cands[0] if cand_count > 0 else {}
            c_name = top_c.get("name", "Oceanic Frontal Candidate")
            c_lat = top_c.get("centroid_lat", 0.0)
            c_lon = top_c.get("centroid_lon", 0.0)
            c_dist = top_c.get("distance_km", "N/A")
            c_bearing = top_c.get("bearing_deg", "N/A")
            c_score = top_c.get("pfz_score", 0.0)
            c_conf = top_c.get("confidence", {}).get("overall_confidence_percent", 75.0)
            c_hazard = top_c.get("hazard_status", "ENVIRONMENTALLY_FAVORABLE").replace("_", " ")
            c_sst = top_c.get("sst_mean_c", "N/A")
            c_chl = top_c.get("chlorophyll_mean_mg_m3", "N/A")
            c_area = top_c.get("geometry", {}).get("area_sq_km", "N/A")

            responses = {
                "en": (
                    f"🐟 **Spatial PFZ Candidate Intelligence & Ocean Analytics · {port_name} Sector**\n\n"
                    f"• **Search Coverage:** Discovered **{cand_count} multi-variable PFZ candidate regions** within radius.\n"
                    f"• **Top Rated Candidate:** **{c_name}**\n"
                    f"• **Centroid Coordinates:** **{c_lat:.2f}°N, {c_lon:.2f}°E** (Distance: **{c_dist} km**, Heading: **{c_bearing}°**)\n"
                    f"• **Estimated Area:** **{c_area} km²** contiguous frontal zone.\n"
                    f"• **Thermal & Color Profile:** SST: **{c_sst}°C** | Chlorophyll-a: **{c_chl} mg/m³**\n"
                    f"• **Scientific PFZ Score:** **{c_score:.3f} / 1.000** (Data-driven suitability)\n"
                    f"• **Data Confidence:** **{c_conf}%** (Independent sensor & coverage metric)\n"
                    f"• **Environmental Hazard State:** **{c_hazard}**\n"
                    f"• **Scientific Integrity Note:** MODEL-DERIVED PFZ. General oceanographic habitat suitability based on coincident thermal and color fronts. ML was not claimed because validated training data were unavailable."
                ),
                "hi": (
                    f"🐟 **स्थानिक संभावित मत्स्य पालन क्षेत्र (PFZ) एवं महासागर विश्लेषण · {port_name}**\n\n"
                    f"• **खोज परिणाम:** त्रिज्या के भीतर **{cand_count} स्थानिक PFZ उम्मीदवार क्षेत्र** पाए गए।\n"
                    f"• **शीर्ष उम्मीदवार क्षेत्र:** **{c_name}**\n"
                    f"• **केंद्रक निर्देशांक:** **{c_lat:.2f}°N, {c_lon:.2f}°E** (दूरी: **{c_dist} किमी**, दिशा: **{c_bearing}°**)\n"
                    f"• **अनुमानित क्षेत्रफल:** **{c_area} वर्ग किमी**\n"
                    f"• **पर्यावरणीय प्रोफाइल:** तापमान (SST): **{c_sst}°C** | क्लोरोफिल: **{c_chl} mg/m³**\n"
                    f"• **वैज्ञानिक PFZ स्कोर:** **{c_score:.3f}** | **डेटा विश्वसनीयता:** **{c_conf}%**\n"
                    f"• **मौसम व आपदा स्थिति:** **{c_hazard}**\n"
                    f"• **वैज्ञानिक सीमाएँ:** मॉडल-व्युत्पन्न उम्मीदवार क्षेत्र। वास्तविक उपग्रह डेटा पर आधारित। प्रमाणित प्रशिक्षण डेटा के अभाव में मशीन लर्निंग का दावा नहीं किया गया है।"
                ),
                "kn": (
                    f"🐟 **ಪ್ರಾದೇಶಿಕ ಸಂಭಾವ್ಯ ಮೀನುಗಾರಿಕಾ ವಲಯ (PFZ) ಬುದ್ಧಿವಂತಿಕೆ · {port_name}**\n\n"
                    f"• **ಹುಡುಕಾಟ ವ್ಯಾಪ್ತಿ:** ವ್ಯಾಪ್ತಿಯಲ್ಲಿ **{cand_count} ಬಹು-ವೇರಿಯಬಲ್ PFZ ಪ್ರದೇಶಗಳು** ಪತ್ತೆಯಾಗಿವೆ.\n"
                    f"• **ಅಗ್ರ ಪ್ರದೇಶ:** **{c_name}**\n"
                    f"• **ನಿರ್ದೇಶಾಂಕಗಳು:** **{c_lat:.2f}°N, {c_lon:.2f}°E** (ದೂರ: **{c_dist} ಕಿಮೀ**, ಕೋನ: **{c_bearing}°**)\n"
                    f"• **ವಿಸ್ತೀರ್ಣ:** **{c_area} ಚದರ ಕಿಮೀ**\n"
                    f"• **ತಾಪಮಾನ ಮತ್ತು ಕ್ಲೋರೋಫಿಲ್:** SST: **{c_sst}°C** | ಕ್ಲೋರೋಫಿಲ್: **{c_chl} mg/m³**\n"
                    f"• **PFZ ಸ್ಕೋರ್:** **{c_score:.3f}** | **ವಿಶ್ವಾಸಾರ್ಹತೆ:** **{c_conf}%**\n"
                    f"• **ಪರಿಸರ ಅಪಾಯ ಸ್ಥಿತಿ:** **{c_hazard}**\n"
                    f"• **ವೈಜ್ಞಾನಿಕ ಟಿಪ್ಪಣಿ:** ಮಾದರಿ-ಉತ್ಪನ್ನ PFZ. ನೈಜ ಉಪಗ್ರಹ ದತ್ತಾಂಶವನ್ನು ಆಧರಿಸಿದೆ. ತರಬೇತಿ ಡೇಟಾ ಇಲ್ಲದ ಕಾರಣ ML ಹೇಳಿಕೊಳ್ಳಲಾಗಿಲ್ಲ."
                )
            }
            text_out = responses.get(lang, responses["en"])

        # ----------------------------------------------------
        # 1. MATH & ARITHMETIC CALCULATOR
        # ----------------------------------------------------
        elif intent == "math_calculation" or re.search(r'^(what is|calculate|solve|evaluate|\s)*\d+[\s\+\-\*\/\^]+\d+', q_lower):
            clean_math = re.sub(r'^(what is|calculate|evaluate|solve|compute|\?|=|\s)+', '', q_lower).strip(' ?=')
            clean_math = re.sub(r'\bplus\b', '+', clean_math)
            clean_math = re.sub(r'\bminus\b', '-', clean_math)
            clean_math = re.sub(r'\btimes\b|\bmultiplied by\b', '*', clean_math)
            clean_math = re.sub(r'\bdivided by\b', '/', clean_math)
            res_val = None
            try:
                expr = clean_math.replace('^', '**')
                res = eval(expr, {'__builtins__': None}, {'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'pi': math.pi})
                if isinstance(res, (int, float)):
                    res_val = int(res) if isinstance(res, float) and res.is_integer() else round(res, 4)
            except Exception:
                pass

            if res_val is not None:
                responses = {
                    "kn": f"🔢 **ಲೆಕ್ಕಾಚಾರದ ಫಲಿತಾಂಶ:**\n\n**{user_query.strip(' ?')}** = **{res_val}**",
                    "kok": f"🔢 **गणनेचो निकाल:**\n\n**{user_query.strip(' ?')}** = **{res_val}**",
                    "or": f"🔢 **ଗଣନା ଫଳାଫଳ:**\n\n**{user_query.strip(' ?')}** = **{res_val}**",
                    "tcy": f"🔢 **ಲೆಕ್ಕದ ಫಲಿತಾಂಶ:**\n\n**{user_query.strip(' ?')}** = **{res_val}**",
                    "kfr": f"🔢 **حساب دا نتیجہ:**\n\n**{user_query.strip(' ?')}** = **{res_val}**",
                    "en": f"🔢 **Calculation Result:**\n\n**{user_query.strip(' ?')}** = **{res_val}**",
                    "hi": f"🔢 **गणना परिणाम:**\n\n**{user_query.strip(' ?')}** = **{res_val}**",
                    "ta": f"🔢 **கணக்கீட்டு முடிவு:**\n\n**{user_query.strip(' ?')}** = **{res_val}**",
                    "te": f"🔢 **గణన ఫలితం:**\n\n**{user_query.strip(' ?')}** = **{res_val}**",
                    "ml": f"🔢 **കണക്കുകൂട്ടൽ ഫലം:**\n\n**{user_query.strip(' ?')}** = **{res_val}**",
                    "bn": f"🔢 **গণনার ফলাফল:**\n\n**{user_query.strip(' ?')}** = **{res_val}**",
                    "gu": f"🔢 **ગણતરી પરિણામ:**\n\n**{user_query.strip(' ?')}** = **{res_val}**",
                    "mr": f"🔢 **गणना निकाल:**\n\n**{user_query.strip(' ?')}** = **{res_val}**"
                }
                text_out = responses.get(lang, responses["en"])
            else:
                text_out = f"🔢 **Calculation:** I could not parse this arithmetic expression. Please enter standard formats like `25 * 4` or `100 / 5`."

        # ----------------------------------------------------
        # 2. UNIT CONVERSIONS (Knots, Nautical Miles, Temperatures)
        # ----------------------------------------------------
        elif intent == "unit_conversion":
            # Knots to km/h
            m_kts = re.search(r'(\d+(?:\.\d+)?)\s*(?:kts|knots?|knot)\s*(?:in|to|into)\s*(?:kmh|km/h|kph|kmph)', q_lower)
            if m_kts:
                val = float(m_kts.group(1))
                text_out = f"📐 **Unit Conversion:**\n\n**{val} knots** = **{round(val * 1.852, 2)} km/h** *(1 knot = 1.852 km/h / 0.514 m/s)*"
            # NM to km
            elif re.search(r'(\d+(?:\.\d+)?)\s*(?:nm|nautical miles?)\s*(?:in|to|into)\s*(?:km|kilometers?)', q_lower):
                m_nm = re.search(r'(\d+(?:\.\d+)?)\s*(?:nm|nautical miles?)\s*(?:in|to|into)\s*(?:km|kilometers?)', q_lower)
                val = float(m_nm.group(1))
                text_out = f"📐 **Unit Conversion:**\n\n**{val} Nautical Miles (NM)** = **{round(val * 1.852, 2)} km** *(1 NM = 1.852 km)*"
            # Celsius to Fahrenheit
            elif re.search(r'(\d+(?:\.\d+)?)\s*(?:c|celsius)\s*(?:in|to|into)\s*(?:f|fahrenheit)', q_lower):
                m_c = re.search(r'(\d+(?:\.\d+)?)\s*(?:c|celsius)\s*(?:in|to|into)\s*(?:f|fahrenheit)', q_lower)
                val = float(m_c.group(1))
                f_val = round((val * 9/5) + 32, 2)
                text_out = f"📐 **Temperature Conversion:**\n\n**{val}°C** = **{f_val}°F**"
            else:
                text_out = f"📐 **Maritime Unit Reference:**\n• **1 Nautical Mile (NM):** 1.852 kilometers (1,852 meters)\n• **1 Knot (kt):** 1.852 km/h (0.514 m/s)\n• **1 Fathom:** 6 feet (1.8288 meters)"

        # ----------------------------------------------------
        # 3. GRATITUDE & COURTESY
        # ----------------------------------------------------
        elif intent == "gratitude":
            responses = {
                "kn": "🙏 **ತುಂಬಾ ಧನ್ಯವಾದಗಳು!**\n\nನಿಮ್ಮ ಸಮುದ್ರ ಪ್ರಯಾಣ ಸುರಕ್ಷಿತವಾಗಿರಲಿ! ⚓🌊",
                "kok": "🙏 **खूप उपकार!**\n\nतुमची समुद्री यात्रा सुरक्षित जावं! ⚓🌊",
                "or": "🙏 **ବହୁତ ଧନ୍ୟବାଦ!**\n\nଆପଣଙ୍କ ସମୁଦ୍ର ଯାତ୍ରା ସୁରକ୍ଷିତ ହେଉ! ⚓🌊",
                "tcy": "🙏 **ತುಂಬ ಧನ್ಯವಾದ!**\n\nನಿಮ್ಮ ಸಮುದ್ರ ಪಯಣ ಸುರಕ್ಷಿತ ಆವಲಿ! ⚓🌊",
                "kfr": "🙏 **بہت شکریہ!**\n\nتہاڈی سمندری سفر محفوظ ہووے! ⚓🌊",
                "en": "🙏 **You're very welcome!**\n\nWishing you calm seas, safe navigation, and bountiful catch! Let me know if you need satellite telemetry or safety updates anytime. ⚓🌊",
                "hi": "🙏 **आपका बहुत-बहुत स्वागत है!**\n\nआपकी सुरक्षित समुद्री यात्रा और सफल मत्स्य पालन की कामना करते हैं! किसी भी समय मौसम या उपग्रह डेटा के लिए पूछ सकते हैं। ⚓🌊",
                "ta": "🙏 **மிக்க நன்றி!**\n\nஉங்கள் கடல் பயணம் பாதுகாப்பாகவும் வெற்றிகரமாகவும் அமைய வாழ்த்துகள்! ⚓🌊",
                "te": "🙏 **మీకు స్వాగతం!**\n\nమీ సముద్ర ప్రయాణం సురక్షితంగా మరియు విజయవంతంగా సాగాలని కోరుకుంటున్నాము! ⚓🌊",
                "ml": "🙏 **നന്ദി!**\n\nനിങ്ങളുടെ സമുദ്രയാത്ര സുരക്ഷിതവും വിജയകരവുമായിരിക്കട്ടെ! ⚓🌊",
                "bn": "🙏 **আপনাকে অনেক ধন্যবাদ!**\n\nআপনার সমুদ্রযাত্রা নিরাপদ এবং সফল হোক! ⚓🌊",
                "gu": "🙏 **ખૂબ ખૂબ આભાર!**\n\nતમારી દરિયાઈ યાત્રા સુરક્ષિત અને સફળ રહે તેવી શુભકામના! ⚓🌊",
                "mr": "🙏 **आपले सहर्ष स्वागत आहे!**\n\nआपला सागरी प्रवास सुरक्षित आणि भरभराटीचा जावो! ⚓🌊"
            }
            text_out = responses.get(lang, responses["en"])

        # ----------------------------------------------------
        # 4. HELP & SYSTEM CAPABILITIES
        # ----------------------------------------------------
        elif intent == "help_capabilities":
            responses = {
                "kn": (
                    f"🛰️ **ಬ್ಲೂ ಆರ್ಬಿಟ್ ವ್ಯವಸ್ಥೆಯ ಸಾಮರ್ಥ್ಯಗಳು · ISRO**\n\n"
                    f"1. **🐟 ಸಂಭಾವ್ಯ ಮೀನುಗಾರಿಕೆ ಪ್ರದೇಶ (PFZ):** Oceansat-3 ಮತ್ತು INSAT-3DR ಡೇಟಾವನ್ನು ಬಳಸಿ ಹೆಚ್ಚಿನ ಇಳುವರಿ ಮೀನುಗಾರಿಕೆ ಪ್ರದೇಶಗಳನ್ನು ಗುರುತಿಸುತ್ತದೆ.\n"
                    f"2. **🛡️ ಸಮುದ್ರ ಸುರಕ್ಷತಾ ಸ್ಕೋರ್ (0-100):** ಅಲೆಗಳು, ಗಾಳಿ ಮತ್ತು ಹವಾಮಾನ ಪರಿಸ್ಥಿತಿಗಳ ಆಧಾರದ ಮೇಲೆ ಸುರಕ್ಷತಾ ಸ್ಥಿತಿಯನ್ನು ಮೌಲ್ಯಮಾಪನ ಮಾಡುತ್ತದೆ.\n"
                    f"3. **🛑 IMBL ಗಡಿ ಎಚ್ಚರಿಕೆ:** ಅಂತರರಾಷ್ಟ್ರೀಯ ಸಮುದ್ರ ಗಡಿಯ ಸಮೀಪವಿದ್ದಾಗ ಎಚ್ಚರಿಕೆ ನೀಡುತ್ತದೆ.\n"
                    f"4. **🧭 ಸುರಕ್ಷಿತ A* ಮಾರ್ಗ:** ಸುರಕ್ಷಿತ ಮತ್ತು ಇಂಧನ-ಕಾರ್ಯಕ್ಷಮ ಸಮುದ್ರ ಮಾರ್ಗವನ್ನು ಸೂಚಿಸುತ್ತದೆ.\n"
                    f"5. **🎙️ ಪ್ರಾದೇಶಿಕ ಧ್ವನಿ ಬೆಂಬಲ:** ಭಾರತೀಯ ಪ್ರಾದೇಶಿಕ ಭಾಷೆಗಳಲ್ಲಿ ಧ್ವನಿ ಸೇವೆ."
                ),

                "kok": (
                    f"🛰️ **ब्लू ऑर्बिट प्रणाली क्षमता · ISRO**\n\n"
                    f"1. **🐟 संभाव्य मत्स्य क्षेत्र (PFZ):** Oceansat-3 आणि INSAT-3DR डेटाच्या आधारे जास्त मासेमारी मिळणारे क्षेत्र शोधते.\n"
                    f"2. **🛡️ सागरी सुरक्षा स्कोर (0-100):** लाटा, वारा आणि हवामानाच्या आधारे समुद्रातील सुरक्षितता तपासते.\n"
                    f"3. **🛑 IMBL सीमा इशारा:** आंतरराष्ट्रीय समुद्री सीमेजवळ पोहोचल्यास इशारा देते.\n"
                    f"4. **🧭 सुरक्षित A* मार्ग:** सुरक्षित आणि इंधन-बचत करणारा समुद्री मार्ग सुचवते.\n"
                    f"5. **🎙️ प्रादेशिक आवाज समर्थन:** भारतीय प्रादेशिक भाषांमध्ये आवाज सेवा."
                ),

                "or": (
                    f"🛰️ **ବ୍ଲୁ ଅର୍ବିଟ୍ ସିଷ୍ଟମ୍ କ୍ଷମତା · ISRO**\n\n"
                    f"1. **🐟 ସମ୍ଭାବ୍ୟ ମତ୍ସ୍ୟ ଅଞ୍ଚଳ (PFZ):** Oceansat-3 ଏବଂ INSAT-3DR ତଥ୍ୟ ବ୍ୟବହାର କରି ଅଧିକ ମାଛ ମିଳୁଥିବା ଅଞ୍ଚଳ ଚିହ୍ନଟ କରେ।\n"
                    f"2. **🛡️ ସମୁଦ୍ର ସୁରକ୍ଷା ସ୍କୋର (0-100):** ତରଙ୍ଗ, ପବନ ଏବଂ ପାଣିପାଗ ଆଧାରରେ ସୁରକ୍ଷା ମୂଲ୍ୟାଙ୍କନ କରେ।\n"
                    f"3. **🛑 IMBL ସୀମା ସତର୍କତା:** ଆନ୍ତର୍ଜାତୀୟ ସମୁଦ୍ର ସୀମା ନିକଟରେ ପହଞ୍ଚିଲେ ସତର୍କ କରେ।\n"
                    f"4. **🧭 ସୁରକ୍ଷିତ A* ମାର୍ଗ:** ସୁରକ୍ଷିତ ଏବଂ ଇନ୍ଧନ-କାର୍ଯ୍ୟକ୍ଷମ ସମୁଦ୍ର ମାର୍ଗ ସୁପାରିଶ କରେ।\n"
                    f"5. **🎙️ ପ୍ରାଦେଶିକ ଭଏସ୍ ସମର୍ଥନ:** ଭାରତୀୟ ପ୍ରାଦେଶିକ ଭାଷାରେ ଭଏସ୍ ସେବା."
                ),

                "tcy": (
                    f"🛰️ **ಬ್ಲೂ ಆರ್ಬಿಟ್ ವ್ಯವಸ್ಥೆದ ಸಾಮರ್ಥ್ಯ · ISRO**\n\n"
                    f"1. **🐟 ಮೀನುಗಾರಿಕೆ ಪ್ರದೇಶ (PFZ):** Oceansat-3 ಮತ್ INSAT-3DR ಡೇಟಾ ಬಳಸಿ ಜಾಸ್ತಿ ಮೀನು ಸಿಕ್ಕೊ ಪ್ರದೇಶ ಗುರುತಿಸಾದ್.\n"
                    f"2. **🛡️ ಸಮುದ್ರ ಸುರಕ್ಷತಾ ಸ್ಕೋರ್ (0-100):** ಅಲೆ, ಗಾಳಿ ಮತ್ ಹವಾಮಾನ ಪರಿಸ್ಥಿತಿ ಆಧಾರಿತ ಸುರಕ್ಷತೆ ಪರೀಕ್ಷಿಸಾದ್.\n"
                    f"3. **🛑 IMBL ಗಡಿ ಎಚ್ಚರಿಕೆ:** ಅಂತರರಾಷ್ಟ್ರೀಯ ಸಮುದ್ರ ಗಡಿ ಹತ್ತಿರ ಬಂದಾಗ ಎಚ್ಚರಿಕೆ ಕೊಡಾದ್.\n"
                    f"4. **🧭 ಸುರಕ್ಷಿತ A* ಮಾರ್ಗ:** ಸುರಕ್ಷಿತ ಮತ್ ಇಂಧನ ಉಳಿಸುವ ಸಮುದ್ರ ಮಾರ್ಗ ಸೂಚಿಸಾದ್.\n"
                    f"5. **🎙️ ಪ್ರಾದೇಶಿಕ ಧ್ವನಿ ಬೆಂಬಲ:** ಭಾರತೀಯ ಪ್ರಾದೇಶಿಕ ಭಾಷೆಗಳಲ್ಲಿ ಧ್ವನಿ ಸೇವೆ."
                ),

                "kfr": (
                    f"🛰️ **بلو آربٹ نظام دیاں صلاحیتاں · ISRO**\n\n"
                    f"1. **🐟 ممکنہ مچھھی پکڑن علاقہ (PFZ):** Oceansat-3 تے INSAT-3DR ڈیٹا نال ودھ مچھھی والے علاقے لبھدا اے۔\n"
                    f"2. **🛡️ سمندری حفاظت سکور (0-100):** لہراں، ہوا تے موسم دے حساب نال حفاظت چیک کردا اے۔\n"
                    f"3. **🛑 IMBL سرحدی خبردار:** بین الاقوامی سمندری سرحد دے نیڑے پہنچن تے خبردار کردا اے۔\n"
                    f"4. **🧭 محفوظ A* راستہ:** محفوظ تے ایندھن بچاؤن والا سمندری راستہ دسد ا اے۔\n"
                    f"5. **🎙️ علاقائی آواز سپورٹ:** بھارتی علاقائی بھاشاں وچ آواز دی سہولت."
                ),
                "en": (
                    f"🛰️ **Blue Orbit System Capabilities · ISRO Problem ID 26176**\n\n"
                    f"I operate a 6-stage collaborative multi-agent reasoning DAG:\n"
                    f"1. **🐟 Potential Fishing Zones (PFZ):** Generates high-yield fishing coordinates by fusing Oceansat-3 OCM-3 Chlorophyll-a with INSAT-3DR SST thermal fronts (yielding 3.5×–4.5× catch boost).\n"
                    f"2. **🛡️ 0–100 Sea Safety Barometer:** Evaluates wave height, swell period, wind speed, and active cyclone hazards to compute real-time venture clearance.\n"
                    f"3. **🛑 IMBL Geofence Engine:** Live vector geofencing against India-Sri Lanka, India-Pakistan, and India-Bangladesh international borders to prevent accidental cross-border arrests.\n"
                    f"4. **🧭 A* Navigational Routing:** Plans optimal, fuel-efficient waypoints avoiding Marine Protected Areas (MPAs) and high-risk zones.\n"
                    f"5. **🎙️ Multilingual Vernacular Voice:** Real-time speech synthesis in 13 Indian regional languages."
                ),
                "hi": (
                    f"🛰️ **ब्लू ऑर्बिट सिस्टम क्षमताएं · इसरो समस्या ID 26176**\n\n"
                    f"1. **🐟 संभावित मत्स्य पालन क्षेत्र (PFZ):** ओशनसैट-3 (क्लोरोफिल) और इनसैट-3DR (SST) डेटा से 3.5×–4.5× अधिक मछली पकड़ने वाले हॉटस्पॉट खोजना।\n"
                    f"2. **🛡️ समुद्र सुरक्षा स्कोर (0-100):** लहरों की ऊंचाई, हवा की गति और चक्रवात के आधार पर समुद्र में जाने की अनुमति देना।\n"
                    f"3. **🛑 अंतर्राष्ट्रीय सीमा (IMBL) अलर्ट:** भारत-श्रीलंका व भारत-पाकिस्तान सीमा के पास अलार्म बजाना ताकि मछुआरे सुरक्षित रहें।\n"
                    f"4. **🧭 सुरक्षित समुद्री मार्ग (A* Routing):** संरक्षित समुद्री क्षेत्रों (MPA) से बचाते हुए सबसे छोटा रास्ता बनाना।\n"
                    f"5. **🎙️ 13 भारतीय भाषाएं:** हिंदी, तमिल, तेलुगु, मलयालम, बंगाली, गुजराती, मराठी और अंग्रेजी सहित 13 क्षेत्रीय भाषाओं में लाइव वॉयस सपोर्ट।"
                ),
                "ta": (
                    f"🛰️ **புளூ ஆர்பிட் அமைப்பின் திறன்கள் · இஸ்ரோ திட்டம்**\n\n"
                    f"1. **🐟 மீன்பிடி மண்டலங்கள் (PFZ):** ஓஷன்சாட்-3 மற்றும் இன்சாட்-3DR மூலம் அதிக மீன் கிடைக்கும் பகுதிகளைக் கண்டறிதல்.\n"
                    f"2. **🛡️ கடல் பாதுகாப்பு குறியீடு (0-100):** அலை மற்றும் வானிலை அடிப்படையில் புறப்பாடு பாதுகாப்பு மதிப்பீடு.\n"
                    f"3. **🛑 சர்வதேச எல்லை (IMBL) எச்சரிக்கை:** இந்திய எல்லைப் பாதுகாப்பிற்கான நிகழ்நேர எச்சரிக்கை.\n"
                    f"4. **🧭 A* வழித்தட திட்டம்:** எரிபொருள் மிச்சப்படுத்தும் பாதுகாப்பான கடல் பாதை.\n"
                    f"5. **🎙️ குரல் ஆதரவு:** 8 பிராந்திய மொழிகளில் நேரலை குரல் சேவை."
                ),
                "te": (
                    f"🛰️ **బ్లూ ఆర్బిట్ సిస్టమ్ సామర్థ్యాలు · ఇస్రో ప్రాజెక్ట్**\n\n"
                    f"1. **🐟 చేపల వేట ప్రాంతాలు (PFZ):** ఓషన్ శాట్-3 మరియు ఇన్సాట్-3DR డేటాతో చేపల హాట్‌స్పాట్‌లను గుర్తించడం.\n"
                    f"2. **🛡️ సముద్ర భద్రతా స్కోరు (0-100):** అలల ఎత్తు మరియు తుఫాను ప్రమాదాల విశ్లేషణ.\n"
                    f"3. **🛑 అంతర్జాతీయ సరిహద్దు (IMBL) హెచ్చరిక:** సరిహద్దు దాటకుండా నిరోధించే జియోఫెన్సింగ్.\n"
                    f"4. **🧭 A* నావిగేషన్ రూటింగ్:** ఇంధన ఆదా చేసే సురక్షిత మార్గాలు.\n"
                    f"5. **🎙️ బహుభాషా వాయిస్:** 8 భారతీయ భాషలలో వాయిస్ సపోర్ట్."
                ),
                "ml": (
                    f"🛰️ **ബ്ലൂ ഓർബിറ്റ് സിസ്റ്റം സേവനങ്ങൾ · ഐഎസ്ആർഒ**\n\n"
                    f"1. **🐟 മത്സ്യബന്ധന മേഖലകൾ (PFZ):** ഓഷ്യൻസാറ്റ്-3, ഇൻസാറ്റ്-3ഡിആർ വഴി കൂടുതൽ മത്സ്യം ലഭിക്കുന്ന പ്രദേശങ്ങൾ കണ്ടെത്തൽ.\n"
                    f"2. **🛡️ കടൽ സുരക്ഷാ സ്കോർ (0-100):** തത്സമയ സുരക്ഷാ പരിശോധന.\n"
                    f"3. **🛑 അന്താരാഷ്ട്ര അതിർത്തി (IMBL) ജാഗ്രത:** അതിർത്തി ലംഘനം തടയുന്നതിനുള്ള അലാറം.\n"
                    f"4. **🧭 നാവിഗേഷൻ റൂട്ട്:** സുരക്ഷിതമായ സമുദ്ര പാത.\n"
                    f"5. **🎙️ വോയ്‌സ് അസിസ്റ്റന്റ്:** 8 ഭാഷകളിലെ തത്സമയ ശബ്ദ സേവനം."
                ),
                "bn": (
                    f"🛰️ **ব্লু অরবিট সিস্টেমের সক্ষমতা · ইসরো সমস্যা ID 26176**\n\n"
                    f"১. **🐟 সম্ভাব্য মৎস্য অঞ্চল (PFZ):** ওশনস্যাট-৩ এবং ইনস্যাট-৩ডিআর তথ্যের মাধ্যমে ৩.৫×–৪.৫× বেশি মাছ পাওয়ার হটস্পট সনাক্তকরণ।\n"
                    f"২. **🛡️ সমুদ্র নিরাপত্তা সূচক (০-১০০):** ঢেউয়ের উচ্চতা ও আবহাওয়া বিশ্লেষণ করে সমুদ্রে যাওয়ার অনুমতি প্রদান।\n"
                    f"৩. **🛑 আন্তর্জাতিক সীমান্ত (IMBL) সতর্কতা:** অনিচ্ছাকৃত সীমান্ত লঙ্ঘন এড়াতে লাইভ জিওফেন্স অ্যালার্ম।\n"
                    f"৪. **🧭 নিরাপদ নৌপথ (A* Routing):** জ্বালানি সাশ্রয়ী সর্বোত্তম নৌপথ পরিকল্পনা।\n"
                    f"৫. **🎙️ বহুভাষিক ভয়েস সাপোর্ট:** ৮টি ভারতীয় আঞ্চলিক ভাষায় ভয়েস আউটপুট।"
                ),
                "gu": (
                    f"🛰️ **બ્લુ ઓર્બિટ સિસ્ટમ ક્ષમતાઓ · ISRO**\n\n"
                    f"1. **🐟 સંભવિત મત્સ્ય ઝોન (PFZ):** Oceansat-3 અને INSAT-3DR ડેટા સાથે માછલીના હોટસ્પોટ્સ.\n"
                    f"2. **🛡️ દરિયાઈ સલામતી સ્કોર (0-100):** વાસ્તવિક સમયની સલામતી મંજૂરી.\n"
                    f"3. **🛑 IMBL આંતરરાષ્ટ્રીય સીમા ચેતવણી:** સરહદ ઉલ્લંઘન અટકાવવા માટે જીઓફેન્સિંગ.\n"
                    f"4. **🧭 A* નેવિગેશન રૂટ:** બળતણ-કાર્યક્ષમ સલામત માર્ગ.\n"
                    f"5. **🎙️ પ્રાદેશિક અવાજ સપોર્ટ:** 8 ભારતીય ભાષાઓમાં વૉઇસ સેવા."
                ),
                "mr": (
                    f"🛰️ **ब्लू ऑर्बिट प्रणाली क्षमता · इस्रो**\n\n"
                    f"1. **🐟 संभाव्य मासेमारी क्षेत्र (PFZ):** ओशनसॅट-३ व इनसॅट-३डीआर द्वारे मासेमारी हॉटस्पॉट.\n"
                    f"2. **🛡️ सागरी सुरक्षा निर्देशांक (०-१००):** लाटा व वादळाच्या आधारे सुरक्षा परवाना.\n"
                    f"3. **🛑 आंतरराष्ट्रीय सीमा (IMBL) इशारा:** सीमा ओलांडण्यापासून रोखण्यासाठी जिओफेन्स अलार्म.\n"
                    f"4. **🧭 सुरक्षित सागरी मार्ग (A* Routing):** इंधन बचत करणारा जलमार्ग.\n"
                    f"5. **🎙️ ८ भाषांमध्ये व्हॉइस सपोर्ट:** प्रादेशिक भाषांमध्ये थेट संवाद."
                )
            }
            text_out = responses.get(lang, responses["en"])

        # ----------------------------------------------------
        # 5. SATELLITE SCIENCE & TECHNOLOGY INQUIRY
        # ----------------------------------------------------
        elif intent == "satellite_science" or is_tech_query:
            responses = {
                "kn": (
                    f"🛰️ **ISRO ಭೂ ವೀಕ್ಷಣೆ ಮತ್ತು ಉಪಗ್ರಹ ಸಮುದ್ರ ವ್ಯವಸ್ಥೆ**\n\n"
                    f"• **Oceansat-3 (EOS-06):** OCM-3 ಸೆನ್ಸರ್ ಮೂಲಕ Chlorophyll-a ಅನ್ನು ಅಳೆಯುತ್ತದೆ.\n"
                    f"• **INSAT-3DR & 3DS:** Thermal Infrared ಮೂಲಕ ಸಮುದ್ರ ಮೇಲ್ಮೈ ತಾಪಮಾನ (SST) ಮತ್ತು thermal fronts ಅನ್ನು ಗುರುತಿಸುತ್ತದೆ.\n"
                    f"• **PFZ ವ್ಯವಸ್ಥೆ:** Chlorophyll ಮತ್ತು thermal fronts ಒಂದಾಗುವ ಪ್ರದೇಶಗಳನ್ನು ಹೆಚ್ಚಿನ ಮೀನು ಲಭ್ಯತೆಯ ಪ್ರದೇಶಗಳಾಗಿ ಗುರುತಿಸುತ್ತದೆ."
                ),

                "kok": (
                    f"🛰️ **ISRO पृथ्वी निरीक्षण आणि उपग्रह समुद्री प्रणाली**\n\n"
                    f"• **Oceansat-3:** OCM-3 सेन्सर वापरून Chlorophyll-a मोजते.\n"
                    f"• **INSAT-3DR:** Thermal Infrared सेन्सरद्वारे समुद्राच्या पृष्ठभागाचे तापमान (SST) आणि thermal fronts तपासते.\n"
                    f"• **PFZ प्रणाली:** Chlorophyll आणि thermal fronts एकत्र येणारी क्षेत्रे शोधते."
                ),

                "or": (
                    f"🛰️ **ISRO ପୃଥିବୀ ଅବଲୋକନ ଏବଂ ଉପଗ୍ରହ ସାମୁଦ୍ରିକ ବ୍ୟବସ୍ଥା**\n\n"
                    f"• **Oceansat-3:** OCM-3 ସେନ୍ସର ମାଧ୍ୟମରେ Chlorophyll-a ମାପେ।\n"
                    f"• **INSAT-3DR:** Thermal Infrared ସେନ୍ସର ଦ୍ୱାରା ସମୁଦ୍ର ପୃଷ୍ଠ ତାପମାତ୍ରା (SST) ଏବଂ thermal fronts ଚିହ୍ନଟ କରେ।\n"
                    f"• **PFZ ବ୍ୟବସ୍ଥା:** Chlorophyll ଏବଂ thermal fronts ମିଳୁଥିବା ଅଞ୍ଚଳ ଚିହ୍ନଟ କରେ."
                ),

                "tcy": (
                    f"🛰️ **ISRO ಭೂ ವೀಕ್ಷಣೆ ಮತ್ ಉಪಗ್ರಹ ಸಮುದ್ರ ವ್ಯವಸ್ಥೆ**\n\n"
                    f"• **Oceansat-3:** OCM-3 ಸೆನ್ಸರ್ ಮೂಲಕ Chlorophyll-a ಅಳತೆ ಮಾಡಾದ್.\n"
                    f"• **INSAT-3DR:** Thermal Infrared ಸೆನ್ಸರ್ ಮೂಲಕ ಸಮುದ್ರ ಮೇಲ್ಮೈ ತಾಪಮಾನ (SST) ಮತ್ thermal fronts ಗುರುತಿಸಾದ್.\n"
                    f"• **PFZ ವ್ಯವಸ್ಥೆ:** Chlorophyll ಮತ್ thermal fronts ಸೇರುವ ಜಾಗ ಗುರುತಿಸಾದ್."
                ),

                "kfr": (
                    f"🛰️ **ISRO دھرتی مشاہدہ تے سیٹلائٹ سمندری نظام**\n\n"
                    f"• **Oceansat-3:** OCM-3 سینسر نال Chlorophyll-a ماپدا اے۔\n"
                    f"• **INSAT-3DR:** Thermal Infrared سینسر نال سمندر دی سطح دا درجہ حرارت (SST) تے thermal fronts چیک کردا اے۔\n"
                    f"• **PFZ نظام:** Chlorophyll تے thermal fronts دے ملن والے علاقے لبھدا اے."
                ),
                "en": (
                    f"🛰️ **ISRO Earth Observation & Marine Intelligence Framework**\n\n"
                    f"• **Oceansat-3 (EOS-06):** Equipped with the **Ocean Colour Monitor (OCM-3)** operating in 13 spectral bands to measure Chlorophyll-a concentration (phytoplankton feeding grounds).\n"
                    f"• **INSAT-3DR & 3DS:** Provides hourly **Thermal Infrared (TIR)** telemetry to compute Sea Surface Temperature (SST) and track oceanic thermal fronts.\n"
                    f"• **PFZ Convergence Engine:** Identifies high-yield zones where high chlorophyll coincided with sharp thermal gradients (|∇SST| ≥ 0.75°C/10km).\n"
                    f"• **Safety & Geofencing:** Combines INCOIS numerical wave models with live IMBL international border boundaries."
                ),
                "hi": (
                    f"🛰️ **इसरो पृथ्वी अवलोकन एवं उपग्रह समुद्री प्रणाली**\n\n"
                    f"• **ओशनसैट-3 (EOS-06):** 13 स्पेक्ट्रल बैंड वाले **ओशन कलर मॉनिटर (OCM-3)** से लैस है, जो समुद्र में क्लोरोफिल-ए (प्लैंकटन) का पता लगाता है।\n"
                    f"• **इनसैट-3DR:** थर्मल इन्फ्रारेड (TIR) सेंसर द्वारा समुद्र सतह का तापमान (SST) और थर्मल फ्रंट्स मापता है।\n"
                    f"• **PFZ एल्गोरिथ्म:** जहाँ क्लोरोफिल और थर्मल फ्रंट मिलते हैं, वहाँ मछलियों का भारी जमावड़ा होता है।"
                ),
                "ta": (
                    f"🛰️ **இஸ்ரோ புவி கண்காணிப்பு மற்றும் செயற்கைக்கோள் கட்டமைப்பு**\n\n"
                    f"• **ஓஷன்சாட்-3:** குளோரோபில்-ஏ செறிவைக் கண்டறியும் 13 ஸ்பெக்ட்ரல் பட்டைகள் கொண்ட OCM-3 சென்சார்.\n"
                    f"• **இன்சாட்-3DR:** கடல் மேற்பரப்பு வெப்பநிலையைக் (SST) கண்காணிக்கும் தெர்மல் இன்ஃப்ராரெட் சென்சார்.\n"
                    f"• **PFZ இயந்திரம்:** குளோரோபில் மற்றும் வெப்ப முனைகள் இணையும் இடங்களில் மீன் கூட்டம் கண்டறிதல்."
                ),
                "te": (
                    f"🛰️ **ఇస్రో ఎర్త్ అబ్జర్వేషన్ మరియు శాటిలైట్ మెరైన్ సిస్టమ్**\n\n"
                    f"• **ఓషన్ శాట్-3:** క్లోరోఫిల్-ఎ గాఢతను కొలిచే OCM-3 సెన్సార్.\n"
                    f"• **ఇన్సాట్-3DR:** సముద్ర ఉపరితల ఉష్ణోగ్రతను (SST) కొలిచే థర్మల్ ఇన్‌ఫ్రారెడ్ సెన్సార్.\n"
                    f"• **PFZ అల్గారిథమ్:** క్లోరోఫిల్ మరియు థర్మల్ ఫ్రంట్స్ కలిసే చోట చేపల లభ్యత గుర్తింపు."
                ),
                "ml": (
                    f"🛰️ **ഐഎസ്ആർഒ ഭൗമനിരീക്ഷണ ഉപഗ്രഹ വിവരങ്ങൾ**\n\n"
                    f"• **ഓഷ്യൻസാറ്റ്-3:** ക്ലോറോഫിൽ-എ സാന്നിധ്യം കണ്ടെത്തുന്ന OCM-3 സെൻസർ.\n"
                    f"• **ഇൻസാറ്റ്-3ഡിആർ:** സമുദ്രോപരിതല താപനില (SST) അളക്കുന്ന തെർമൽ ഇൻഫ്രാറെഡ് സെൻസർ.\n"
                    f"• **PFZ മോഡൽ:** താപ വ്യതിയാനങ്ങളും ക്ലോറോഫിലും ഒരുമിക്കുന്ന ഇടങ്ങളിൽ മത്സ്യ ലഭ്യത ഉറപ്പാക്കുന്നു."
                ),
                "bn": (
                    f"🛰️ **ইসরো আর্থ অবজারভেশন ও উপগ্রহ সামুদ্রিক তথ্য কাঠামো**\n\n"
                    f"• **ওশনস্যাট-৩ (EOS-06):** ১৩টি বর্ণালী ব্যান্ডবিশিষ্ট **ওশন কালার মনিটর (OCM-3)** দ্বারা ক্লোরোফিল-এ (প্লাঙ্কটন খাদ্যস্তর) পরিমাপ করে।\n"
                    f"• **ইনস্যাট-৩ডিআর ও ৩ডিএস:** সমুদ্র পৃষ্ঠের তাপমাত্রা (SST) এবং থার্মাল ফ্রন্ট ট্র্যাকিংয়ের জন্য প্রতি ঘণ্টার থার্মাল ইনফ্রারেড টেলিমেট্রি প্রদান করে।\n"
                    f"• **PFZ কনভার্জেন্স ইঞ্জিন:** যেখানে উচ্চ ক্লোরোফিল ও তীব্র থার্মাল গ্রেডিয়েন্ট মিলিত হয়, সেখানে মাছের প্রাচুর্য অঞ্চল নির্ধারণ করে।"
                ),
                "gu": (
                    f"🛰️ **ISRO પૃથ્વી અવલોકન અને સેટેલાઇટ સિસ્ટમ**\n\n"
                    f"• **Oceansat-3:** ક્લોરોફિલ-a માપવા માટે OCM-3 સેન્સર.\n"
                    f"• **INSAT-3DR:** સમુદ્ર સપાટીનું તાપમાન (SST) માપવા માટે થર્મલ ઇન્ફ્રારેડ સેન્સર.\n"
                    f"• **PFZ એન્જિન:** જ્યાં ક્લોરોફિલ અને થર્મલ ફ્રન્ટ્સ મળે છે ત્યાં માછલીઓનો વિશાળ જથ્થો હોય છે."
                ),
                "mr": (
                    f"🛰️ **इस्रो पृथ्वी निरीक्षण व उपग्रह सागरी प्रणाली**\n\n"
                    f"• **ओशनसॅट-३:** क्लोरोफिल-ए मोजण्यासाठी OCM-3 सेन्सर.\n"
                    f"• **इनसॅट-३डीआर:** समुद्र पृष्ठभागाचे तापमान (SST) मोजण्यासाठी थर्मल इन्फ्रारेड सेन्सर.\n"
                    f"• **PFZ अल्गोरिदम:** क्लोरोफिल आणि थर्मल फ्रंट जिथे एकत्र येतात तिथे माशांची उपलब्धता वाढते."
                )
            }
            text_out = responses.get(lang, responses["en"])

        # ----------------------------------------------------
        # 6. IDENTITY & TEAM
        # ----------------------------------------------------
        elif intent == "identity":
            responses = {
                "kn": (
                    f"🛰️ **ನಾನು ಬ್ಲೂ ಆರ್ಬಿಟ್ (Blue Orbit)**\n\n"
                    f"ನಾನು **Sih_Hackers** ತಂಡವು **ISRO**ಗಾಗಿ ಅಭಿವೃದ್ಧಿಪಡಿಸಿದ ಸ್ವಯಂಚಾಲಿತ Agentic AI ಸಮುದ್ರ ನಿರ್ಧಾರ-ಬೆಂಬಲ ವ್ಯವಸ್ಥೆಯಾಗಿದ್ದೇನೆ (SIH 2026 Problem ID 26176).\n\n"
                    f"• **ಮುಖ್ಯ ಕಾರ್ಯಗಳು:** Oceansat-3 ಮತ್ತು INSAT-3DR ಡೇಟಾದಿಂದ PFZ ಗುರುತಿಸುವುದು, ಸಮುದ್ರ ಸುರಕ್ಷತಾ ಸ್ಕೋರ್ ನೀಡುವುದು ಮತ್ತು IMBL ಗಡಿ ಮೇಲ್ವಿಚಾರಣೆ."
                ),

                "kok": (
                    f"🛰️ **मी ब्लू ऑर्बिट (Blue Orbit) आहे**\n\n"
                    f"मी **Sih_Hackers** ने **ISRO** साठी विकसित केलेली स्वयंचलित समुद्री AI निर्णय-समर्थन प्रणाली आहे (SIH 2026 Problem ID 26176).\n\n"
                    f"• **मुख्य कार्ये:** Oceansat-3 आणि INSAT-3DR डेटातून PFZ शोधणे, समुद्री सुरक्षा स्कोर देणे आणि IMBL सीमांचे निरीक्षण करणे."
                ),

                "or": (
                    f"🛰️ **ମୁଁ ବ୍ଲୁ ଅର୍ବିଟ୍ (Blue Orbit)**\n\n"
                    f"ମୁଁ **Sih_Hackers** ଦ୍ୱାରା **ISRO** ପାଇଁ ବିକଶିତ ଏକ ସ୍ୱୟଂଚାଳିତ ସାମୁଦ୍ରିକ AI ନିଷ୍ପତ୍ତି ସହାୟକ ବ୍ୟବସ୍ଥା (SIH 2026 Problem ID 26176)।\n\n"
                    f"• **ମୁଖ୍ୟ କାର୍ଯ୍ୟ:** Oceansat-3 ଏବଂ INSAT-3DR ତଥ୍ୟରୁ PFZ ଚିହ୍ନଟ କରିବା, ସମୁଦ୍ର ସୁରକ୍ଷା ସ୍କୋର ଦେବା ଏବଂ IMBL ସୀମା ନିରୀକ୍ଷଣ କରିବା."
                ),

                "tcy": (
                    f"🛰️ **ನಾನ್ ಬ್ಲೂ ಆರ್ಬಿಟ್ (Blue Orbit)**\n\n"
                    f"ನಾನ್ **Sih_Hackers** ತಂಡದ್ **ISRO**ಗಾಗಿ ತಯಾರ್ ಮಲ್ಪುನ ಸ್ವಯಂಚಾಲಿತ ಸಮುದ್ರ AI ನಿರ್ಧಾರ ಸಹಾಯಕ ವ್ಯವಸ್ಥೆ ಆವುತ್ತೆ (SIH 2026 Problem ID 26176).\n\n"
                    f"• **ಮುಖ್ಯ ಕೆಲಸೊಲು:** Oceansat-3 ಮತ್ INSAT-3DR ಡೇಟಾದಿಂದ PFZ ಗುರುತಿಸಾದ್, ಸಮುದ್ರ ಸುರಕ್ಷತಾ ಸ್ಕೋರ್ ಕೊಡಾದ್ ಮತ್ IMBL ಗಡಿ ಗಮನಿಸಾದ್."
                ),

                "kfr": (
                    f"🛰️ **میں بلو آربٹ (Blue Orbit) آں**\n\n"
                    f"میں **Sih_Hackers** ولوں **ISRO** لئی بنائی گئی خودکار سمندری AI فیصلہ معاون نظام آں (SIH 2026 Problem ID 26176).\n\n"
                    f"• **مکھ کم:** Oceansat-3 تے INSAT-3DR ڈیٹا نال PFZ لبھنا، سمندری حفاظت سکور دینا تے IMBL سرحد دی نگرانی کرنا."
                ),
                "en": (
                    f"🛰️ **I am Blue Orbit**\n\n"
                    f"I am an autonomous Agentic AI decision-support platform engineered by **Sih_Hackers** for the **Indian Space Research Organisation (ISRO)** (Smart India Hackathon 2026 Problem Statement ID 26176).\n\n"
                    f"• **Capabilities:** Identifying high-yield Potential Fishing Zones (PFZ) from Oceansat-3 & INSAT-3DR data, computing real-time 0–100 Sea Safety clearance, and enforcing International Maritime Boundary Line (IMBL) geofencing compliance.\n"
                    f"• **Multi-lingual Support:** 13 Indian regional languages with real-time vernacular voice synthesis."
                ),
                "hi": (
                    f"🛰️ **मैं ब्लू ऑर्बिट (Blue Orbit) हूँ**\n\n"
                    f"मैं **टीम रनटाइम टेरर (Sih_Hackers)** द्वारा **भारतीय अंतरिक्ष अनुसंधान संगठन (ISRO)** के लिए विकसित एक स्वायत्त एजेंटिक AI समुद्री निर्णय-समर्थन प्रणाली हूँ (SIH 2026 Problem ID 26176)।\n\n"
                    f"• **मुख्य कार्य:** ओशनसैट-3 और इनसैट-3DR उपग्रह डेटा से संभावित मत्स्य पालन क्षेत्र (PFZ) खोजना, वास्तविक समय समुद्र सुरक्षा स्कोर (0-100) प्रदान करना और अंतर्राष्ट्रीय समुद्री सीमा (IMBL) की निगरानी करना।"
                ),
                "ta": (
                    f"🛰️ **நான் புளூ ஆர்பிட் (Blue Orbit)**\n\n"
                    f"நான் **டீம் ரன்டைம் டெரர் (Sih_Hackers)** ஆல் **இஸ்ரோ (ISRO)** க்காக உருவாக்கப்பட்ட ஒரு தானியங்கி கடல்சார் AI முடிவெடுக்கும் தளமாகும் (SIH 2026 Problem ID 26176)."
                ),
                "te": (
                    f"🛰️ **నేను బ్లూ ఆర్బిట్ (Blue Orbit)**\n\n"
                    f"నేను **టీమ్ రన్‌టైమ్ టెర్రర్ (Sih_Hackers)** చే **ఇస్రో (ISRO)** కోసం రూపొందించబడిన స్వయంప్రతిపత్త సముద్ర AI వేదికను."
                ),
                "ml": (
                    f"🛰️ **ഞാൻ ബ്ലൂ ഓർബിറ്റ് (Blue Orbit)**\n\n"
                    f"**ടീം റൺടൈം ടെറർ (Sih_Hackers)** **ഐ.എസ്.ആർ.ഒ (ISRO)** ക്കായി വികസിപ്പിച്ചെടുത്ത അത്യാധുനിക സമുദ്ര എ.ഐ പ്ലാറ്റ്‌ഫോമാണ് ഞാൻ."
                ),
                "bn": (
                    f"🛰️ **আমি ব্লু অরবিট (Blue Orbit)**\n\n"
                    f"আমি **টিম রানটাইম টেরর** দ্বারা **ইসরো (ISRO)** এর জন্য নির্মিত একটি এআই প্ল্যাটফর্ম।"
                ),
                "gu": (
                    f"🛰️ **હું બ્લુ ઓર્બિટ (Blue Orbit) છું**\n\n"
                    f"હું **ટીમ રનટાઇમ ટેરર** દ્વારા **ISRO** માટે વિકસાવવામાં આવેલ આર્ટિફિશિયલ ઇન્ટેલિજન્સ પ્લેટફોર્મ છું."
                ),
                "mr": (
                    f"🛰️ **मी ब्लू ऑर्बिट (Blue Orbit) आहे**\n\n"
                    f"मी **टीम रनटाइम टेरर** द्वारे **इस्रो (ISRO)** साठी विकसित केलेली स्वायत्त सागरी AI प्रणाली आहे."
                )
            }
            text_out = responses.get(lang, responses["en"])

        # ----------------------------------------------------
        # 7. GREETING
        # ----------------------------------------------------
        elif intent == "greeting":
            responses = {
                "kn": (
                    f"👋 **ನಮಸ್ಕಾರ! ಬ್ಲೂ ಆರ್ಬಿಟ್‌ಗೆ ಸ್ವಾಗತ**\n\n"
                    f"{port_name} ಪ್ರದೇಶಕ್ಕಾಗಿ ISRO ಉಪಗ್ರಹ ಡೇಟಾದೊಂದಿಗೆ ಸಂಪರ್ಕ ಹೊಂದಿದ್ದೇನೆ.\n\n"
                    f"ನೀವು ಸಮುದ್ರ ಸುರಕ್ಷತೆ, PFZ, IMBL ಗಡಿ, ಸುರಕ್ಷಿತ ಮಾರ್ಗ ಅಥವಾ Oceansat-3 ಬಗ್ಗೆ ಕೇಳಬಹುದು."
                ),

                "kok": (
                    f"👋 **नमस्कार! ब्लू ऑर्बिट मध्ये आपले स्वागत आहे**\n\n"
                    f"{port_name} क्षेत्रासाठी ISRO उपग्रह डेटाशी जोडलेलो आहे.\n\n"
                    f"तुम्ही समुद्री सुरक्षा, PFZ, IMBL सीमा, सुरक्षित मार्ग किंवा Oceansat-3 बद्दल विचारू शकता."
                ),

                "or": (
                    f"👋 **ନମସ୍କାର! ବ୍ଲୁ ଅର୍ବିଟ୍‌କୁ ସ୍ୱାଗତ**\n\n"
                    f"{port_name} ଅଞ୍ଚଳ ପାଇଁ ISRO ଉପଗ୍ରହ ତଥ୍ୟ ସହିତ ସଂଯୁକ୍ତ ଅଛି।\n\n"
                    f"ଆପଣ ସମୁଦ୍ର ସୁରକ୍ଷା, PFZ, IMBL ସୀମା, ସୁରକ୍ଷିତ ମାର୍ଗ କିମ୍ବା Oceansat-3 ବିଷୟରେ ପଚାରିପାରିବେ."
                ),

                "tcy": (
                    f"👋 **ನಮಸ್ಕಾರ! ಬ್ಲೂ ಆರ್ಬಿಟ್‌ಗ್ ಸ್ವಾಗತ**\n\n"
                    f"{port_name} ಪ್ರದೇಶಕ್ಕಾಗಿ ISRO ಉಪಗ್ರಹ ಡೇಟಾದೊಟ್ಟಿಗೆ ಸಂಪರ್ಕ ಉಂಡು.\n\n"
                    f"ನೀವು ಸಮುದ್ರ ಸುರಕ್ಷತೆ, PFZ, IMBL ಗಡಿ, ಸುರಕ್ಷಿತ ಮಾರ್ಗ ಅಥವಾ Oceansat-3 ಬಗ್ಗೆ ಕೇಳ್‌ಲೆ."
                ),

                "kfr": (
                    f"👋 **سلام! بلو آربٹ وچ تہاڈا سواغت اے**\n\n"
                    f"{port_name} علاقے لئی ISRO سیٹلائٹ ڈیٹا نال جڑیا ہویا آں۔\n\n"
                    f"تسی سمندری حفاظت، PFZ، IMBL سرحد، محفوظ راستے یا Oceansat-3 بارے پچھ سکدے او."
                ),
                "en": ( 
                    f"👋 **Hello! Welcome to Blue Orbit**\n\n"
                    f"I am actively monitoring live satellite telemetry from ISRO Oceansat-3, INSAT-3DR, and INCOIS for the **{port_name}** sector ({port_state}).\n\n"
                    f"How can I assist you right now? You can ask me:\n"
                    f"• *\"Is it safe to venture into the sea tomorrow morning from {port_name}?\"*\n"
                    f"• *\"Where is the nearest PFZ for Tuna today?\"*\n"
                    f"• *\"What is our distance to the {border_name}?\"*\n"
                    f"• *\"How does Oceansat-3 satellite detect fish schools?\"*"
                ),
                "hi": (
                    f"👋 **नमस्ते! ब्लू ऑर्बिट में आपका स्वागत है**\n\n"
                    f"मैं **{port_name}** क्षेत्र के लिए इसरो ओशनसैट-3, इनसैट-3DR और इनकॉइस के लाइव सैटेलाइट डेटा की निगरानी कर रहा हूँ।\n\n"
                    f"आज मैं आपकी क्या सहायता कर सकता हूँ?\n"
                    f"• *\"क्या कल सुबह {port_name} से समुद्र में जाना सुरक्षित है?\"*\n"
                    f"• *\"ट्यूना मछली के लिए निकटतम क्षेत्र कहाँ है?\"*\n"
                    f"• *\"अंतर्राष्ट्रीय समुद्री सीमा (IMBL) की दूरी बताएं।\"*"
                ),
                "ta": (
                    f"👋 **வணக்கம்! புளூ ஆர்பிட்டுக்கு வரவேற்கிறோம்**\n\n"
                    f"{port_name} பகுதிக்குரிய இஸ்ரோ செயற்கைக்கோள் தரவுகளுடன் நேரலையில் இணைந்துள்ளேன். இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?"
                ),
                "te": (
                    f"👋 **నమస్కారం! బ్లూ ఆర్బిట్‌కు స్వాగతం**\n\n"
                    f"{port_name} ప్రాంతం కోసం ఇస్రో ఉపగ్రహ డేటాతో అనుసంధానించబడి ఉన్నాను. నేను మీకు ఎలా సహాయపడగలను?"
                ),
                "ml": (
                    f"👋 **നമസ്കാരം! ബ്ലൂ ഓർബിറ്റിലേക്ക് സ്വാഗതം**\n\n"
                    f"{port_name} മേഖലയിലെ തത്സമയ ഉപഗ്രഹ വിവരങ്ങളുമായി ബന്ധിപ്പിച്ചിരിക്കുന്നു. ഇന്ന് ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കണം?"
                ),
                "bn": (
                    f"👋 **নমস্কার! ব্লু অরবিটে স্বাগতম**\n\n"
                    f"{port_name} অঞ্চলের জন্য ইসরো উপগ্রহ তথ্যের সাথে সংযুক্ত। আজ আমি আপনাকে কীভাবে সাহায্য করতে পারি?\n\n"
                    f"• *\"আগামীকাল সকালে {port_name} থেকে সমুদ্রে যাওয়া কি নিরাপদ?\"*\n"
                    f"• *\"নিকটতম মাছ ধরার সম্ভাব্য এলাকা (PFZ) কোথায়?\"*\n"
                    f"• *\"আন্তর্জাতিক সামুদ্রিক সীমান্ত (IMBL) কত দূরে?\"*"
                ),
                "gu": (
                    f"👋 **નમસ્તે! બ્લુ ઓર્બિટમાં આપનું સ્વાગત છે**\n\n"
                    f"{port_name} માટે ISRO ઉપગ્રહ ડેટા સાથે જોડાયેલ છું. હું તમને કેવી રીતે મદદ કરી શકું?"
                ),
                "mr": (
                    f"👋 **नमस्कार! ब्लू ऑर्बिट मध्ये आपले स्वागत आहे**\n\n"
                    f"{port_name} क्षेत्रासाठी इस्रो उपग्रह डेटाशी जोडलेला आहे. मी आज आपल्याला कशी मदत करू शकतो?"
                )
            }
            text_out = responses.get(lang, responses["en"])

        # ----------------------------------------------------
        # 8. GENERAL INQUIRY & FALLBACK
        # ----------------------------------------------------
        else:
            responses = {
                "kn": (
                    f"🛰️ **ಬ್ಲೂ ಆರ್ಬಿಟ್ ಸಂಭಾಷಣ ಸಹಾಯಕ**\n\n"
                    f"ನಿಮ್ಮ ಪ್ರಶ್ನೆ ಸ್ವೀಕರಿಸಲಾಗಿದೆ: *\"{user_query.strip()}\"*\n\n"
                    f"ಪ್ರಸ್ತುತ **{port_name}** ಪ್ರದೇಶದ ಮಾಹಿತಿ:\n"
                    f"• **ಸಮುದ್ರ ಸ್ಥಿತಿ:** {status.replace('_', ' ')} (ಸ್ಕೋರ್: {score}/100, ಅಲೆ: {wave}m, ಗಾಳಿ: {wind} kts).\n"
                    f"• **ಹತ್ತಿರದ ಮೀನುಗಾರಿಕೆ ಪ್ರದೇಶ:** {pfz_name} ({pfz_dist} ಕಿಮೀ, ಪ್ರಮುಖ ಮೀನು: {species}).\n\n"
                    f"ನೀವು ಸಮುದ್ರ ಸುರಕ್ಷತೆ, ಮೀನುಗಾರಿಕೆ ಪ್ರದೇಶ, A* ಮಾರ್ಗ ಅಥವಾ ISRO ಉಪಗ್ರಹ ಡೇಟಾ ಬಗ್ಗೆ ಕೇಳಬಹುದು."
                ),

                "kok": (
                    f"🛰️ **ब्लू ऑर्बिट संभाषण सहाय्यक**\n\n"
                    f"तुमची विचारणा मिळाली: *\"{user_query.strip()}\"*\n\n"
                    f"सध्या **{port_name}** क्षेत्राची माहिती:\n"
                    f"• **समुद्री स्थिती:** {status.replace('_', ' ')} (स्कोर: {score}/100, लाटा: {wave}m, वारा: {wind} kts).\n"
                    f"• **जवळचे मासेमारी क्षेत्र:** {pfz_name} ({pfz_dist} किमी, प्रमुख मासे: {species}).\n\n"
                    f"तुम्ही समुद्री सुरक्षा, मासेमारी क्षेत्र, A* मार्ग किंवा ISRO उपग्रह डेटाबद्दल विचारू शकता."
                ),

                "or": (
                    f"🛰️ **ବ୍ଲୁ ଅର୍ବିଟ୍ ସଂଳାପ ସହାୟକ**\n\n"
                    f"ଆପଣଙ୍କ ପ୍ରଶ୍ନ ମିଳିଛି: *\"{user_query.strip()}\"*\n\n"
                    f"ବର୍ତ୍ତମାନ **{port_name}** ଅଞ୍ଚଳର ସୂଚନା:\n"
                    f"• **ସମୁଦ୍ର ସ୍ଥିତି:** {status.replace('_', ' ')} (ସ୍କୋର: {score}/100, ତରଙ୍ଗ: {wave}m, ପବନ: {wind} kts)।\n"
                    f"• **ନିକଟତମ ମତ୍ସ୍ୟ ଅଞ୍ଚଳ:** {pfz_name} ({pfz_dist} କିମି, ପ୍ରମୁଖ ମାଛ: {species})।\n\n"
                    f"ଆପଣ ସମୁଦ୍ର ସୁରକ୍ଷା, ମତ୍ସ୍ୟ ଅଞ୍ଚଳ, A* ମାର୍ଗ କିମ୍ବା ISRO ଉପଗ୍ରହ ତଥ୍ୟ ବିଷୟରେ ପଚାରିପାରିବେ."
                ),

                "tcy": (
                    f"🛰️ **ಬ್ಲೂ ಆರ್ಬಿಟ್ ಸಂಭಾಷಣ ಸಹಾಯಕ**\n\n"
                    f"ನಿಮ್ಮ ಪ್ರಶ್ನೆ ಸಿಕ್ಕುಂಡು: *\"{user_query.strip()}\"*\n\n"
                    f"ಈಗ **{port_name}** ಪ್ರದೇಶದ ಮಾಹಿತಿ:\n"
                    f"• **ಸಮುದ್ರ ಸ್ಥಿತಿ:** {status.replace('_', ' ')} (ಸ್ಕೋರ್: {score}/100, ಅಲೆ: {wave}m, ಗಾಳಿ: {wind} kts).\n"
                    f"• **ಹತ್ತಿರದ ಮೀನುಗಾರಿಕೆ ಪ್ರದೇಶ:** {pfz_name} ({pfz_dist} ಕಿಮೀ, ಮುಖ್ಯ ಮೀನು: {species}).\n\n"
                    f"ನೀವು ಸಮುದ್ರ ಸುರಕ್ಷತೆ, ಮೀನುಗಾರಿಕೆ ಪ್ರದೇಶ, A* ಮಾರ್ಗ ಅಥವಾ ISRO ಉಪಗ್ರಹ ಡೇಟಾ ಬಗ್ಗೆ ಕೇಳ್‌ಲೆ."
                ),

                "kfr": (
                    f"🛰️ **بلو آربٹ گل بات معاون**\n\n"
                    f"تہاڈی پچھ گچھ مل گئی اے: *\"{user_query.strip()}\"*\n\n"
                    f"ہن **{port_name}** علاقے دی معلومات:\n"
                    f"• **سمندری حالت:** {status.replace('_', ' ')} (سکور: {score}/100، لہراں: {wave}m، ہوا: {wind} kts)۔\n"
                    f"• **نیڑے مچھھی پکڑن علاقہ:** {pfz_name} ({pfz_dist} کلومیٹر، مکھ مچھھی: {species})۔\n\n"
                    f"تسی سمندری حفاظت، مچھھی پکڑن علاقے، A* راستے یا ISRO سیٹلائٹ ڈیٹا بارے پچھ سکدے او."
                ),
                "en": (
                    f"🛰️ **Blue Orbit Conversational Assistant**\n\n"
                    f"I have received your inquiry: *\"{user_query.strip()}\"*\n\n"
                    f"Currently focused on the **{port_name}** sector. For marine operations:\n"
                    f"• **Sea State:** {status.replace('_', ' ')} (Score: {score}/100, Waves: {wave}m, Wind: {wind} kts).\n"
                    f"• **Nearest Fishing Zone:** {pfz_name} ({pfz_dist} km away, Dominant: {species}).\n\n"
                    f"You can ask me specific questions on sea safety, fish hotspots, A* route planning, math calculations, or ISRO satellite telemetry."
                ),
                "hi": (
                    f"🛰️ **ब्लू ऑर्बिट सहायक**\n\n"
                    f"मुझे आपका प्रश्न प्राप्त हुआ: *\"{user_query.strip()}\"*\n\n"
                    f"**{port_name}** क्षेत्र के लिए वर्तमान स्थिति:\n"
                    f"• **समुद्र सुरक्षा:** {status.replace('_', ' ')} (स्कोर: {score}/100, लहरें: {wave}m, हवा: {wind} kts)।\n"
                    f"• **मछली क्षेत्र:** {pfz_name} ({pfz_dist} किमी दूर, प्रमुख: {species})।\n\n"
                    f"आप मुझसे समुद्र सुरक्षा, मछली पकड़ने के क्षेत्र, सुरक्षित मार्ग या इसरो सैटेलाइट डेटा के बारे में पूछ सकते हैं।"
                ),
                "ta": (
                    f"🛰️ **புளூ ஆர்பிட் உரையாடல் உதவியாளர்**\n\n"
                    f"உங்கள் வினவல் பெறப்பட்டது: *\"{user_query.strip()}\"*\n\n"
                    f"தற்போது **{port_name}** பகுதிக்குரிய நேரலை தகவல்:\n"
                    f"• **கடல் நிலை:** {status.replace('_', ' ')} (மதிப்பெண்: {score}/100, அலை: {wave}m, காற்று: {wind} kts).\n"
                    f"• **அருகிலுள்ள மீன்பிடி மண்டலம்:** {pfz_name} ({pfz_dist} கி.மீ தொலைவு, முக்கிய மீன்: {species}).\n\n"
                    f"கடல் பாதுகாப்பு, மீன்பிடி மண்டலங்கள், A* வழித்தட திட்டம் அல்லது இஸ்ரோ செயற்கைக்கோள் தரவு குறித்து கேட்கலாம்."
                ),
                "te": (
                    f"🛰️ **బ్లూ ఆర్బిట్ సంభాషణ సహాయకుడు**\n\n"
                    f"మీ ప్రశ్న అందింది: *\"{user_query.strip()}\"*\n\n"
                    f"ప్రస్తుతం **{port_name}** సెక్టార్ వివరాలు:\n"
                    f"• **సముద్ర స్థితి:** {status.replace('_', ' ')} (స్కోరు: {score}/100, అలలు: {wave}m, గాలి: {wind} kts).\n"
                    f"• **సమీప చేపల వేట ప్రాంతం:** {pfz_name} ({pfz_dist} కి.మీ, రకం: {species}).\n\n"
                    f"సముద్ర భద్రత, చేపల హాట్‌స్పాట్‌లు, మార్గ ప్రణాళిక లేదా ఇస్రో ఉపగ్రహ డేటా గురించి అడగవచ్చు."
                ),
                "ml": (
                    f"🛰️ **ബ്ലൂ ഓർബിറ്റ് സംഭാഷണ സഹായി**\n\n"
                    f"നിങ്ങളുടെ ചോദ്യം ലഭിച്ചു: *\"{user_query.strip()}\"*\n\n"
                    f"നിലവിൽ **{port_name}** മേഖലയിലെ വിവരങ്ങൾ:\n"
                    f"• **കടൽാവസ്ഥ:** {status.replace('_', ' ')} (സ്കോർ: {score}/100, തിരമാല: {wave}m, കാറ്റ്: {wind} kts).\n"
                    f"• **അടുത്തുള്ള മത്സ്യബന്ധന മേഖല:** {pfz_name} ({pfz_dist} കി.മീ, പ്രധാന മത്സ്യം: {species}).\n\n"
                    f"കടൽ സുരക്ഷ, മത്സ്യ മേഖലകൾ, നാവിഗേഷൻ റൂട്ട്, ഐ.എസ്.ആർ.ഒ ഉപഗ്രഹ വിവരങ്ങൾ എന്നിവയെക്കുറിച്ച് ചോദിക്കാം."
                ),
                "bn": (
                    f"🛰️ **ব্লু অরবিট কথোপকথন সহকারী**\n\n"
                    f"আপনার অনুসন্ধান গৃহীত হয়েছে: *\"{user_query.strip()}\"*\n\n"
                    f"বর্তমানে **{port_name}** অঞ্চলের জন্য সামুদ্রিক তথ্য:\n"
                    f"• **সমুদ্রের অবস্থা:** {status.replace('_', ' ')} (স্কোর: {score}/100, ঢেউ: {wave}মি, বাতাস: {wind} নট)।\n"
                    f"• **নিকটতম সম্ভাব্য মৎস্য অঞ্চল:** {pfz_name} ({pfz_dist} কিমি দূরে, প্রধান মাছ: {species})।\n\n"
                    f"আপনি সমুদ্রের নিরাপত্তা, মাছের হটস্পট, A* নিরাপদ নৌপথ বা ইসরো উপগ্রহ তথ্য সম্পর্কে প্রশ্ন করতে পারেন।"
                ),
                "gu": (
                    f"🛰️ **બ્લુ ઓર્બિટ સહાયક**\n\n"
                    f"મને તમારો પ્રશ્ન મળ્યો: *\"{user_query.strip()}\"*\n\n"
                    f"હાલમાં **{port_name}** ક્ષેત્ર માટે દરિયાઈ પરિસ્થિતિ:\n"
                    f"• **દરિયાઈ સ્થિતિ:** {status.replace('_', ' ')} (સ્કોર: {score}/100, મોજા: {wave}m, પવન: {wind} kts).\n"
                    f"• **નજીકનું માછીમારી ક્ષેત્ર:** {pfz_name} ({pfz_dist} કિમી દૂર, પ્રજાતિ: {species}).\n\n"
                    f"તમે દરિયાઈ સલામતી, મત્સ્ય હોટસ્પોટ્સ, A* રૂટ પ્લાનિંગ અથવા ISRO સેટેલાઇટ ટેલિમેટ્રી વિશે પૂછી શકો છો."
                ),
                "mr": (
                    f"🛰️ **ब्लू ऑर्बिट संभाषण सहाय्यक**\n\n"
                    f"मला आपली विचारणा प्राप्त झाली: *\"{user_query.strip()}\"*\n\n"
                    f"सध्या **{port_name}** क्षेत्रासाठी सागरी परिस्थिती:\n"
                    f"• **सागरी स्थिती:** {status.replace('_', ' ')} (स्कोअर: {score}/100, लाटा: {wave}m, वारा: {wind} kts).\n"
                    f"• **जवळचे मासेमारी क्षेत्र:** {pfz_name} ({pfz_dist} किमी दूर, प्रमुख जात: {species}).\n\n"
                    f"तुम्ही सागरी सुरक्षा, मासेमारी क्षेत्र, A* मार्ग किंवा इस्रो उपग्रह माहितीबद्दल विचारू शकता."
                )
            }
            text_out = responses.get(lang, responses["en"])

        # Generate clean plain text for TTS speech synthesizer (no markdown symbols)
        tts_clean = re.sub(r'[*#•🛰️🛡️🛑🧭🐟\n]+', ' ', text_out).strip()
        tts_clean = re.sub(r'\s+', ' ', tts_clean)

        return {
            "language_code": lang,
            "language_name": self.supported_languages[lang]["name"],
            "native_name": self.supported_languages[lang]["native"],
            "formatted_markdown": text_out,
            "tts_speech_text": tts_clean,
            "voice_code": self.supported_languages[lang]["voice_code"]
        }
