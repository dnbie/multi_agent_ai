"""
Emergency Agent - Smart emergency assistant
Provides nearest hospitals, shows emergency contacts, opens Maps, generates help message
Reuses: BrowserAgent._maps_route(), LLMTool
Now includes user-specific emergency contacts from their profile settings.
"""

import re
import webbrowser
from typing import List, Dict
from .base_agent import BaseAgent, AgentResult


# ── Static emergency data ─────────────────────────────────────────────────────

EMERGENCY_CONTACTS = [
    {"name": "Police",          "number": "100"},
    {"name": "Ambulance",       "number": "108"},
    {"name": "Fire",            "number": "101"},
    {"name": "Women Helpline",  "number": "1091"},
    {"name": "Disaster",        "number": "1078"},
    {"name": "Child Helpline",  "number": "1098"},
    {"name": "Senior Citizen",  "number": "14567"},
]

HOSPITALS_BY_CITY = {
    "chennai":    ["Apollo Hospitals (Greams Road)", "Fortis Malar Hospital", "MIOT International"],
    "coimbatore": ["PSG Hospitals", "Kovai Medical Center", "Sri Ramakrishna Hospital"],
    "mumbai":     ["Lilavati Hospital", "Breach Candy Hospital", "Kokilaben Hospital"],
    "delhi":      ["AIIMS Delhi", "Max Super Speciality", "Fortis Escorts Heart Institute"],
    "bangalore":  ["Manipal Hospital", "Apollo BGS Hospital", "Narayana Health City"],
    "hyderabad":  ["KIMS Hospital", "Yashoda Hospital", "Apollo Hospital Jubilee Hills"],
    "kolkata":    ["AMRI Hospital", "Fortis Hospital", "Columbia Asia"],
}

EMERGENCY_KEYWORDS = {
    "accident":   "road accident",
    "fire":       "fire emergency",
    "heart":      "cardiac emergency",
    "chest pain": "cardiac emergency",
    "robbery":    "theft/robbery",
    "attacked":   "assault/attack",
    "drowning":   "drowning",
    "poison":     "poisoning",
    "fall":       "fall injury",
    "bleeding":   "severe bleeding",
    "unconscious":"medical emergency",
}


def get_user_emergency_info():
    """Get user's personal emergency contacts from their profile settings"""
    try:
        from config import get_user_emergency_info_from_session
        return get_user_emergency_info_from_session()
    except Exception:
        return None


class EmergencyAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Emergency Agent",
            description="Smart emergency assistant — contacts, hospital, maps, AI guidance"
        )

    def get_capabilities(self) -> List[str]:
        return [
            "Detect emergency type from command",
            "Show national emergency numbers",
            "Show user's personal emergency contacts",
            "Show nearest hospitals for your city",
            "Open Google Maps to nearest hospital",
            "AI-generated emergency guidance",
        ]

    def execute(self, task: str, **kwargs) -> AgentResult:
        self._start_execution(task)
        try:
            emergency_type = self._detect_emergency(task)
            
            # Get user's emergency info from profile
            user_emergency_info = get_user_emergency_info()
            
            # Try to get city from user settings first, then from task
            city = kwargs.get("city")
            if not city and user_emergency_info:
                city = user_emergency_info.get('city', '')
            if not city:
                city = self._extract_city(task)
            
            hospitals = self._get_hospitals(city)
            
            # Add user's preferred hospital if set
            if user_emergency_info and user_emergency_info.get('preferred_hospital'):
                preferred = user_emergency_info['preferred_hospital']
                if preferred not in hospitals:
                    hospitals = [f"⭐ {preferred} (Your Preferred)"] + hospitals
            
            guidance = self._get_guidance(emergency_type, city, user_emergency_info)

            # Open maps to nearest hospital
            maps_url = ""
            if hospitals:
                from urllib.parse import quote_plus
                dest = f"hospital near {city}" if city else "nearest hospital"
                maps_url = f"https://www.google.com/maps/search/{quote_plus(dest)}"
                try:
                    webbrowser.open(maps_url)
                except Exception:
                    pass

            # Build emergency contacts text (include user's personal contacts)
            contacts_text = "\n".join(
                f"{c['name']}: {c['number']}" for c in EMERGENCY_CONTACTS[:5]
            )
            
            # Add user's personal emergency contacts
            personal_contacts_text = ""
            if user_emergency_info:
                primary = user_emergency_info.get('primary', {})
                secondary = user_emergency_info.get('secondary', {})
                
                personal_contacts = []
                if primary.get('name') and primary.get('phone'):
                    relation = f" ({primary.get('relation')})" if primary.get('relation') else ""
                    personal_contacts.append(f"⭐ {primary['name']}{relation}: {primary['phone']}")
                if secondary.get('name') and secondary.get('phone'):
                    personal_contacts.append(f"⭐ {secondary['name']}: {secondary['phone']}")
                
                if personal_contacts:
                    personal_contacts_text = "\n\nYOUR EMERGENCY CONTACTS:\n" + "\n".join(personal_contacts)
            
            hospitals_text = "\n".join(f"- {h}" for h in hospitals) if hospitals else "Search nearby hospitals on Google Maps."

            # Add medical info if available
            medical_info_text = ""
            if user_emergency_info:
                med_info = []
                if user_emergency_info.get('blood_group'):
                    med_info.append(f"Blood Group: {user_emergency_info['blood_group']}")
                if user_emergency_info.get('medical_conditions'):
                    med_info.append(f"Medical Conditions: {user_emergency_info['medical_conditions']}")
                if user_emergency_info.get('home_address'):
                    med_info.append(f"Home Address: {user_emergency_info['home_address']}")
                
                if med_info:
                    medical_info_text = "\n\nYOUR MEDICAL INFO:\n" + "\n".join(med_info)

            message = (
                f"EMERGENCY DETECTED: {emergency_type.upper()}\n\n"
                f"NATIONAL EMERGENCY CONTACTS:\n{contacts_text}"
                f"{personal_contacts_text}\n\n"
                f"NEARBY HOSPITALS{' (' + city.title() + ')' if city else ''}:\n{hospitals_text}"
                f"{medical_info_text}\n\n"
                f"GUIDANCE:\n{guidance}"
            )

            result = self._create_result(True, message, data={
                "emergency_type": emergency_type,
                "city": city,
                "contacts": EMERGENCY_CONTACTS,
                "user_emergency_contacts": user_emergency_info,
                "hospitals": hospitals,
                "maps_url": maps_url,
                "guidance": guidance,
            })
        except Exception as e:
            result = self._create_result(False, f"Emergency agent error: {str(e)}", error=str(e))

        self._end_execution(result)
        return result

    # ── helpers ───────────────────────────────────────────────────────────────

    def _detect_emergency(self, text: str) -> str:
        lower = text.lower()
        for keyword, etype in EMERGENCY_KEYWORDS.items():
            if keyword in lower:
                return etype
        return "general emergency"

    def _get_hospitals(self, city: str) -> List[str]:
        if not city:
            return []
        return HOSPITALS_BY_CITY.get(city.lower().strip(), [])

    def _get_guidance(self, emergency_type: str, city: str, user_info: dict = None) -> str:
        try:
            llm = self.get_llm()
            
            # Build context from user medical info
            medical_context = ""
            if user_info:
                if user_info.get('blood_group'):
                    medical_context += f" The person's blood group is {user_info['blood_group']}."
                if user_info.get('medical_conditions'):
                    medical_context += f" Known medical conditions: {user_info['medical_conditions']}."
            
            prompt = (
                f"Someone is experiencing a '{emergency_type}' emergency{' in ' + city if city else ''}.{medical_context}\n"
                "Provide 3-4 concise, actionable first-response steps. Be calm and direct. "
                "Include when to call 108 (ambulance) or 100 (police). Max 80 words."
            )
            return llm.generate_text(prompt, temperature=0.3)
        except Exception:
            return (
                "1. Stay calm and ensure your safety first.\n"
                "2. Call 108 (Ambulance) or 100 (Police) immediately.\n"
                "3. Do not move injured persons unless in immediate danger.\n"
                "4. Alert nearby people for help."
            )

    def _extract_city(self, text: str) -> str:
        known = list(HOSPITALS_BY_CITY.keys())
        lower = text.lower()
        for city in known:
            if city in lower:
                return city
        m = re.search(r'in\s+([a-z]+)', lower)
        if m:
            return m.group(1)
        return ""
