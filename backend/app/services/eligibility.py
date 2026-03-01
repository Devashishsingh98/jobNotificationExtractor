"""Eligibility matching engine.

Compares a user profile against a notification's requirements and returns
whether the user is eligible, partially eligible, or not eligible.
"""

from datetime import date, datetime
from typing import Optional


# Education level hierarchy (higher index = higher level)
EDUCATION_LEVELS = {
    "10th": 1,
    "12th": 2,
    "Diploma": 2,
    "Graduation": 3,
    "Post Graduation": 4,
    "PhD": 5,
}

# Standard age relaxation by category
DEFAULT_AGE_RELAXATION = {
    "General": 0,
    "EWS": 0,
    "OBC": 3,
    "SC": 5,
    "ST": 5,
}


def calculate_age(dob: date | str, reference_date: Optional[date] = None) -> int:
    """Calculate age from DOB."""
    if isinstance(dob, str):
        dob = datetime.strptime(dob, "%Y-%m-%d").date()
    ref = reference_date or date.today()
    age = ref.year - dob.year
    if (ref.month, ref.day) < (dob.month, dob.day):
        age -= 1
    return age


def check_eligibility(user_profile: dict, notification: dict) -> dict:
    """
    Check if a user is eligible for a notification.

    Returns:
        {
            "status": "eligible" | "partial" | "not_eligible",
            "reasons": ["reason1", "reason2", ...]
        }
    """
    reasons = []
    is_eligible = True
    has_partial = False

    # --- Age check ---
    user_dob = user_profile.get("dob")
    max_age = notification.get("max_age")
    min_age = notification.get("min_age")

    if user_dob and max_age:
        user_age = calculate_age(user_dob)
        user_category = user_profile.get("category", "General")

        # Get age relaxation
        age_relaxation = notification.get("age_relaxation") or DEFAULT_AGE_RELAXATION
        relaxation = age_relaxation.get(user_category, 0)
        effective_max_age = max_age + relaxation

        if user_age > effective_max_age:
            is_eligible = False
            reasons.append(
                f"Age {user_age} exceeds max {effective_max_age} "
                f"(base {max_age} + {relaxation}yr {user_category} relaxation)"
            )
        elif user_age > max_age:
            has_partial = True
            reasons.append(
                f"Age {user_age} eligible only with {user_category} relaxation "
                f"(+{relaxation}yrs)"
            )
        else:
            reasons.append(f"Age {user_age} ✓ (max {effective_max_age})")

        if min_age and user_age < min_age:
            is_eligible = False
            reasons.append(f"Below minimum age {min_age}")

    # --- Education check ---
    user_edu = user_profile.get("education_level")
    required_edu = notification.get("education_required")

    if user_edu and required_edu:
        user_level = EDUCATION_LEVELS.get(user_edu, 0)
        required_level = EDUCATION_LEVELS.get(required_edu, 0)

        if required_level > 0:
            if user_level >= required_level:
                reasons.append(f"Education {user_edu} ✓ (requires {required_edu})")
            else:
                is_eligible = False
                reasons.append(f"Requires {required_edu}, you have {user_edu}")

    # --- Category vacancy check ---
    user_category = user_profile.get("category", "General")
    vacancy_by_cat = notification.get("vacancy_by_category") or {}

    if vacancy_by_cat:
        cat_vacancies = vacancy_by_cat.get(user_category)
        if cat_vacancies is not None:
            if cat_vacancies > 0:
                reasons.append(f"{cat_vacancies} vacancies for {user_category} ✓")
            else:
                has_partial = True
                reasons.append(f"No vacancies listed for {user_category}")
        else:
            reasons.append(f"Category-wise vacancy data available")

    # --- State-specific check ---
    user_state = user_profile.get("state")
    notification_org = notification.get("organization", "")
    exam_type = notification.get("exam_type", "")

    # State PSC mapping (organization acronym -> state)
    STATE_PSC_MAP = {
        "BPSC": "Bihar",
        "UPPSC": "Uttar Pradesh",
        "MPPSC": "Madhya Pradesh",
        "RPSC": "Rajasthan",
        "WBPSC": "West Bengal",
        "KPSC": "Karnataka",
        "TNPSC": "Tamil Nadu",
        "APPSC": "Andhra Pradesh",
        "TSPSC": "Telangana",
        "HPPSC": "Himachal Pradesh",
        "UKPSC": "Uttarakhand",
        "CGPSC": "Chhattisgarh",
        "JPSC": "Jharkhand",
        "GPSC": "Gujarat",
        "MPSC": "Maharashtra",
        "OSSSC": "Odisha",
    }

    # If it's a state exam, check state match
    if exam_type == "State" and notification_org in STATE_PSC_MAP:
        required_state = STATE_PSC_MAP[notification_org]
        if user_state:
            if user_state == required_state:
                reasons.append(f"State {user_state} ✓ (matches {notification_org})")
            else:
                # Most state exams require state residency
                is_eligible = False
                reasons.append(
                    f"Requires {required_state} residency, your state: {user_state}"
                )
        else:
            has_partial = True
            reasons.append(f"State exam for {required_state} (update your state in profile)")

    # --- Determine status ---
    if not is_eligible:
        status = "not_eligible"
    elif has_partial:
        status = "partial"
    else:
        status = "eligible"

    return {"status": status, "reasons": reasons}
