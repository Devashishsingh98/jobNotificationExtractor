"""Notification text parser.

Extracts structured data from Telegram post text using regex + heuristics.
Falls back to Gemini for complex/ambiguous posts.
"""

import re
import json
from datetime import datetime
from typing import Optional
import google.generativeai as genai
from app.config import get_settings


# Known government organizations
KNOWN_ORGS = {
    "UPSC": "Union Public Service Commission",
    "SSC": "Staff Selection Commission",
    "IBPS": "Institute of Banking Personnel Selection",
    "RBI": "Reserve Bank of India",
    "RRB": "Railway Recruitment Board",
    "NTA": "National Testing Agency",
    "DRDO": "Defence Research & Development Organisation",
    "ISRO": "Indian Space Research Organisation",
    "BPSC": "Bihar Public Service Commission",
    "UPPSC": "Uttar Pradesh Public Service Commission",
    "MPPSC": "Madhya Pradesh Public Service Commission",
    "RPSC": "Rajasthan Public Service Commission",
    "WBPSC": "West Bengal Public Service Commission",
    "KPSC": "Karnataka Public Service Commission",
    "TNPSC": "Tamil Nadu Public Service Commission",
    "APPSC": "Andhra Pradesh Public Service Commission",
    "TSPSC": "Telangana State Public Service Commission",
    "HPPSC": "Himachal Pradesh Public Service Commission",
    "UKPSC": "Uttarakhand Public Service Commission",
    "CGPSC": "Chhattisgarh Public Service Commission",
    "JPSC": "Jharkhand Public Service Commission",
    "GPSC": "Gujarat Public Service Commission",
    "MPSC": "Maharashtra Public Service Commission",
    "OSSSC": "Odisha Sub-Staff Selection Commission",
    "SBI": "State Bank of India",
    "NABARD": "National Bank for Agriculture and Rural Development",
    "LIC": "Life Insurance Corporation",
    "EPFO": "Employees' Provident Fund Organisation",
    "FCI": "Food Corporation of India",
    "SAIL": "Steel Authority of India Limited",
    "ONGC": "Oil and Natural Gas Corporation",
    "NTPC": "National Thermal Power Corporation",
    "AAI": "Airports Authority of India",
}

# Job notification keywords
JOB_KEYWORDS = [
    "recruitment", "vacancy", "vacancies", "notification", "bharti",
    "apply online", "last date", "admit card", "result", "exam date",
    "application form", "sarkari", "govt job", "government job",
    "total post", "total posts", "age limit", "eligibility",
    "qualification", "selection process", "official website",
    "important dates", "how to apply", "new recruitment",
]

# Exam type classifiers
EXAM_TYPE_KEYWORDS = {
    "Central": ["upsc", "ssc", "nta", "central", "ministry", "department"],
    "Banking": ["ibps", "sbi", "rbi", "nabard", "bank", "banking"],
    "Railway": ["rrb", "railway", "rail"],
    "Defence": ["army", "navy", "air force", "drdo", "defence", "defense", "military"],
    "State": ["psc", "state", "bpsc", "uppsc", "mppsc", "rpsc"],
    "PSU": ["psu", "sail", "ongc", "ntpc", "bhel", "iocl", "gail"],
}

# Initialize Gemini
try:
    settings = get_settings()
    genai.configure(api_key=settings.google_api_key)
    gemini_model = genai.GenerativeModel('gemini-2.0-flash')
except Exception:
    gemini_model = None  # Fallback disabled if API key not configured


def is_job_notification(text: str) -> bool:
    """Check if a Telegram post is a job notification."""
    text_lower = text.lower()
    matches = sum(1 for kw in JOB_KEYWORDS if kw in text_lower)
    return matches >= 2  # At least 2 keywords match


def parse_with_gemini(text: str) -> dict:
    """
    Use Gemini AI to extract structured data from notification text.

    Returns dict with extracted fields or empty dict on failure.
    """
    prompt = f"""You are analyzing a government job notification from India. Extract the following information from the text and return ONLY valid JSON (no markdown, no explanations):

{{
  "title": "Main title/heading of the notification",
  "organization": "Organization acronym (e.g., UPSC, SSC, IBPS, RBI, RRB, etc.)",
  "exam_type": "One of: Central, Banking, Railway, Defence, State, PSU, Other",
  "last_date": "Last date in YYYY-MM-DD format",
  "min_age": 18,
  "max_age": 35,
  "education_required": "One of: 10th, 12th, Diploma, Graduation, Post Graduation, PhD",
  "total_vacancies": 100
}}

Important:
- Use null for missing fields
- For organization, use the acronym only (UPSC, not "Union Public Service Commission")
- Date must be YYYY-MM-DD format
- Ages must be integers
- Education must exactly match one of the listed options
- Return ONLY the JSON object, no other text

Notification text:
{text}"""

    try:
        response = gemini_model.generate_content(prompt)
        # Extract JSON from response
        response_text = response.text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        data = json.loads(response_text)

        # Validate and clean the data
        result = {}
        if data.get("title"):
            result["title"] = str(data["title"])[:500]
        if data.get("organization"):
            result["organization"] = str(data["organization"])[:50]
        if data.get("exam_type"):
            result["exam_type"] = str(data["exam_type"])
        if data.get("last_date"):
            # Validate date format
            try:
                datetime.strptime(data["last_date"], "%Y-%m-%d")
                result["last_date"] = data["last_date"]
            except ValueError:
                pass
        if data.get("min_age") and isinstance(data["min_age"], int):
            result["min_age"] = data["min_age"]
        if data.get("max_age") and isinstance(data["max_age"], int):
            result["max_age"] = data["max_age"]
        if data.get("education_required"):
            result["education_required"] = str(data["education_required"])
        if data.get("total_vacancies") and isinstance(data["total_vacancies"], int):
            result["total_vacancies"] = data["total_vacancies"]

        return result
    except Exception as e:
        print(f"Gemini parsing error: {e}")
        return {}


def parse_notification(text: str) -> dict:
    """
    Extract structured data from notification text.

    Returns dict with fields matching the notifications table.
    Uses regex first, falls back to Gemini AI for missing fields.
    """
    result = {
        "title": extract_title(text),
        "organization": extract_organization(text),
        "exam_type": classify_exam_type(text),
        "last_date": extract_last_date(text),
        "min_age": None,
        "max_age": None,
        "education_required": extract_education(text),
        "total_vacancies": extract_vacancies(text),
        "raw_text": text,
        "is_processed": True,
    }

    # Extract age limits
    age = extract_age_limits(text)
    if age:
        result["min_age"] = age.get("min")
        result["max_age"] = age.get("max")

    # AI fallback: If critical fields are missing, try Gemini
    missing_critical_fields = (
        not result["title"] or
        not result["organization"] or
        not result["last_date"]
    )

    if missing_critical_fields and gemini_model:
        try:
            ai_result = parse_with_gemini(text)
            # Fill in missing fields only
            if not result["title"] and ai_result.get("title"):
                result["title"] = ai_result["title"]
            if not result["organization"] and ai_result.get("organization"):
                result["organization"] = ai_result["organization"]
            if not result["last_date"] and ai_result.get("last_date"):
                result["last_date"] = ai_result["last_date"]
            if not result["min_age"] and ai_result.get("min_age"):
                result["min_age"] = ai_result["min_age"]
            if not result["max_age"] and ai_result.get("max_age"):
                result["max_age"] = ai_result["max_age"]
            if not result["education_required"] and ai_result.get("education_required"):
                result["education_required"] = ai_result["education_required"]
            if not result["total_vacancies"] and ai_result.get("total_vacancies"):
                result["total_vacancies"] = ai_result["total_vacancies"]
        except Exception as e:
            # AI fallback failed, continue with regex results
            print(f"Gemini fallback failed: {e}")

    return result


def extract_title(text: str) -> str:
    """Extract the main title/heading from the notification text."""
    lines = text.strip().split("\n")
    # First non-empty line is usually the title
    for line in lines[:5]:
        line = line.strip()
        if len(line) > 10 and len(line) < 200:
            # Clean up common prefixes/emojis
            cleaned = re.sub(r"^[🔔📢📋🏛️✅❌⭐🔥💥📌]+\s*", "", line)
            if cleaned:
                return cleaned
    return lines[0].strip() if lines else "Untitled Notification"


def extract_organization(text: str) -> Optional[str]:
    """Identify the government organization from the text."""
    text_upper = text.upper()
    for abbrev, full_name in KNOWN_ORGS.items():
        if abbrev in text_upper:
            return abbrev
    return None


def classify_exam_type(text: str) -> str:
    """Classify the notification into an exam type category."""
    text_lower = text.lower()
    for exam_type, keywords in EXAM_TYPE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return exam_type
    return "Other"


def extract_last_date(text: str) -> Optional[str]:
    """Extract the last date of application."""
    # Common patterns for dates
    patterns = [
        r"last\s+date[:\s-]+(\d{1,2}[\s/.-]\w+[\s/.-]\d{2,4})",
        r"last\s+date[:\s-]+(\d{1,2}[\s/.-]\d{1,2}[\s/.-]\d{2,4})",
        r"apply\s+before[:\s-]+(\d{1,2}[\s/.-]\w+[\s/.-]\d{2,4})",
        r"deadline[:\s-]+(\d{1,2}[\s/.-]\w+[\s/.-]\d{2,4})",
        r"(\d{1,2}[\s/.-]\d{1,2}[\s/.-]\d{4})\s*\(?\s*last\s+date",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1).strip()
            parsed = try_parse_date(date_str)
            if parsed:
                return parsed.strftime("%Y-%m-%d")

    return None


def extract_age_limits(text: str) -> Optional[dict]:
    """Extract min/max age from text."""
    patterns = [
        r"age\s*(?:limit)?[:\s-]*(\d{1,2})\s*(?:to|-)\s*(\d{1,2})\s*(?:years?)?",
        r"(\d{1,2})\s*(?:to|-)\s*(\d{1,2})\s*years?\s*(?:of\s+age)?",
        r"minimum\s+age[:\s-]*(\d{1,2})",
        r"maximum\s+age[:\s-]*(\d{1,2})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                return {"min": int(groups[0]), "max": int(groups[1])}
            elif "minimum" in pattern.lower():
                return {"min": int(groups[0]), "max": None}
            elif "maximum" in pattern.lower():
                return {"min": None, "max": int(groups[0])}

    return None


def extract_education(text: str) -> Optional[str]:
    """Extract education requirement."""
    edu_patterns = {
        "PhD": r"\bph\.?d\b|\bdoctorate\b",
        "Post Graduation": r"\bpost\s*graduat\w+\b|\bm\.?a\b|\bm\.?sc\b|\bm\.?tech\b|\bm\.?b\.?a\b|\bmasters?\b",
        "Graduation": r"\bgraduat\w+\b|\bb\.?a\b|\bb\.?sc\b|\bb\.?tech\b|\bb\.?e\b|\bbachelor\b|\bdegree\b",
        "Diploma": r"\bdiploma\b",
        "12th": r"\b12th\b|\binter\w*\b|\bhigher\s+secondary\b|\b10\+2\b",
        "10th": r"\b10th\b|\bmatric\w*\b|\bhigh\s+school\b|\bsecondary\b",
    }

    for level, pattern in edu_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            return level

    return None


def extract_vacancies(text: str) -> Optional[int]:
    """Extract total number of vacancies."""
    patterns = [
        r"total\s+(?:posts?|vacancies?|seats?)[:\s-]*(\d+)",
        r"(\d+)\s+(?:posts?|vacancies?|seats?)",
        r"(?:posts?|vacancies?|seats?)[:\s-]*(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            if 1 <= num <= 500000:  # Sanity check
                return num

    return None


def extract_urls(text: str) -> list[str]:
    """Extract all URLs from text."""
    url_pattern = r"https?://[^\s<>\"')\]]+"
    return re.findall(url_pattern, text)


def try_parse_date(date_str: str) -> Optional[datetime]:
    """Try multiple date formats to parse a string."""
    formats = [
        "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
        "%d/%m/%y", "%d-%m-%y",
        "%d %B %Y", "%d %b %Y",
        "%d %B, %Y", "%d %b, %Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None
