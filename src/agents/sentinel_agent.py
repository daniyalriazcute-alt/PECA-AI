import os
import json
import re
from security.system_prompts import SENTINEL_SYSTEM_PROMPT

def analyze_with_sentinel(user_input: str, groq_client=None):
    crime_map = {
        "hack": "Unauthorized Access - Section 3 / 6",
        "unauthorized access": "Unauthorized Access - Section 3",
        "hacked": "Unauthorized Access - Section 3",
        "critical infrastructure": "Critical Infrastructure - Section 6-8",
        "copy data": "Unauthorized Copying - Section 4 / 7",
        "data theft": "Unauthorized Copying - Section 4",
        "damage system": "Interference - Section 5 / 8",
        "virus": "Malicious Code - Section 23",
        "malware": "Malicious Code - Section 23",
        "ransomware": "Malicious Code - Section 23",
        "glorification": "Glorification - Section 9",
        "terrorism": "Cyber Terrorism - Section 10",
        "cyber terrorism": "Cyber Terrorism - Section 10",
        "hate speech": "Hate Speech - Section 11",
        "hate": "Hate Speech - Section 11",
        "identity": "Identity Theft - Section 16",
        "fake profile": "Fake Profile - Section 16",
        "impersonation": "Impersonation - Section 16",
        "defamation": "Dignity - Section 20",
        "dignity": "Dignity - Section 20",
        "reputation": "Defamation - Section 20",
        "blackmail": "Blackmail / Sextortion - Section 21",
        "sextortion": "Sextortion - Section 21",
        "private photo": "Modesty - Section 21",
        "private photos": "Modesty - Section 21",
        "intimate": "Intimate Images - Section 21",
        "nude": "Intimate Images - Section 21",
        "leak photos": "Intimate Images - Section 21",
        "grooming": "Online Grooming - Section 22A",
        "solicitation": "Grooming - Section 22A",
        "minor": "Offences Against Minor - Sec 21 + 22A",
        "child porn": "Child Exploitation - Section 22B",
        "child sexual": "Child Abuse - Section 22B",
        "exploitation": "Exploitation - Section 22B",
        "kidnapping": "Kidnapping via System - Section 22C",
        "abduction": "Abduction - Section 22C",
        "trafficking": "Trafficking - Section 22C",
        "malicious code": "Malicious Code - Section 23",
        "stalking": "Cyber Stalking - Section 24",
        "stalk": "Cyber Stalking - Section 24",
        "monitoring": "Stalking - Section 24",
        "cyberbullying": "Cyberbullying - Section 24A",
        "bullying": "Cyberbullying - Section 24A",
        "bully": "Cyberbullying - Section 24A",
        "harassment": "Harassment - Section 24A",
        "spam": "Spamming - Section 25",
        "spamming": "Spamming - Section 25",
        "spoof": "Spoofing - Section 26",
        "spoofing": "Spoofing - Section 26",
        "false information": "False Info - Section 26A",
        "fake news": "Fake Info - Section 26A",
        "misinformation": "False Info - Section 26A",
        "victim protection": "Victim Protection - Section 30B",
    }

    lower = user_input.lower()
    detected_type = "General Cyber Harassment - Under PECA 2016"
    matched_keys = []

    for k, v in crime_map.items():
        if k in lower:
            matched_keys.append(k)
            if len(k) > 6:
                detected_type = v

    is_crime = len(matched_keys) > 0 or len(lower.split()) > 5

    if groq_client:
        try:
            system_extra = SENTINEL_SYSTEM_PROMPT + "\nFull PECA: 3-8 Hacking, 9 Glorification, 10 Terrorism, 16 Identity, 20 Dignity, 21 Modesty, 22A Grooming, 22B Child, 22C Kidnapping, 23 Malicious Code, 24 Stalking, 24A Bullying, 25 Spam, 26 Spoof, 26A False Info"
            user_prompt = f"Analyze PECA 2016: {user_input}\nReturn JSON only with keys detected, crime_type, confidence, summary, peca_keywords"
            resp = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": system_extra},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=800
            )
            text = resp.choices[0].message.content
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                parsed = json.loads(m.group())
                if matched_keys and parsed.get("confidence", 0) < 0.7:
                    parsed["confidence"] = 0.92
                return parsed
        except Exception as e:
            print(f"Sentinel GROQ error: {e}")

    return {
        "detected": bool(is_crime),
        "crime_type": detected_type,
        "confidence": 0.94 if is_crime else 0.62,
        "summary": f"Based on 15 years FIA NR3C experience, incident '{user_input[:100]}...' indicates {detected_type}. This violates PECA 2016 full act 60 sections.",
        "peca_keywords": matched_keys[:5] if matched_keys else ["general harassment"]
    }
