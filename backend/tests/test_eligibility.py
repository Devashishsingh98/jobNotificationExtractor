"""Tests for eligibility matching engine."""

import pytest
from datetime import date
from app.services.eligibility import check_eligibility, calculate_age


class TestCalculateAge:
    def test_basic_age(self):
        age = calculate_age("2000-01-01", reference_date=date(2026, 3, 2))
        assert age == 26

    def test_birthday_not_yet(self):
        age = calculate_age("2000-06-15", reference_date=date(2026, 3, 2))
        assert age == 25

    def test_birthday_passed(self):
        age = calculate_age("2000-01-01", reference_date=date(2026, 3, 2))
        assert age == 26

    def test_same_day_birthday(self):
        age = calculate_age("2000-03-02", reference_date=date(2026, 3, 2))
        assert age == 26

    def test_date_object_input(self):
        age = calculate_age(date(1995, 5, 10), reference_date=date(2026, 3, 2))
        assert age == 30


class TestEligibilityAge:
    """Test age-based eligibility checking."""

    def test_eligible_within_age(self):
        profile = {"dob": "2000-01-01", "category": "General"}
        notification = {"min_age": 21, "max_age": 32}
        result = check_eligibility(profile, notification)
        assert result["status"] == "eligible"

    def test_not_eligible_over_age(self):
        profile = {"dob": "1985-01-01", "category": "General"}
        notification = {"min_age": 21, "max_age": 32}
        result = check_eligibility(profile, notification)
        assert result["status"] == "not_eligible"
        assert any("exceeds" in r for r in result["reasons"])

    def test_not_eligible_under_age(self):
        profile = {"dob": "2010-01-01", "category": "General"}
        notification = {"min_age": 21, "max_age": 32}
        result = check_eligibility(profile, notification)
        assert result["status"] == "not_eligible"
        assert any("Below minimum" in r for r in result["reasons"])

    def test_obc_relaxation(self):
        """OBC gets +3 years relaxation."""
        profile = {"dob": "1992-01-01", "category": "OBC"}  # age 34
        notification = {"min_age": 21, "max_age": 32}
        result = check_eligibility(profile, notification)
        # 34 <= 32 + 3 = 35, so partial (eligible with relaxation)
        assert result["status"] == "partial"
        assert any("relaxation" in r for r in result["reasons"])

    def test_sc_relaxation(self):
        """SC gets +5 years relaxation."""
        profile = {"dob": "1990-01-01", "category": "SC"}  # age 36
        notification = {"min_age": 21, "max_age": 32}
        result = check_eligibility(profile, notification)
        # 36 <= 32 + 5 = 37, so partial
        assert result["status"] == "partial"

    def test_sc_over_relaxation(self):
        """SC age exceeds even with relaxation."""
        profile = {"dob": "1985-01-01", "category": "SC"}  # age 41
        notification = {"min_age": 21, "max_age": 32}
        result = check_eligibility(profile, notification)
        # 41 > 32 + 5 = 37
        assert result["status"] == "not_eligible"

    def test_custom_age_relaxation(self):
        """Notification with custom relaxation overrides defaults."""
        profile = {"dob": "1991-01-01", "category": "OBC"}  # age 35
        notification = {
            "min_age": 21,
            "max_age": 32,
            "age_relaxation": {"OBC": 5, "SC": 7},
        }
        result = check_eligibility(profile, notification)
        # 35 <= 32 + 5 = 37, partial
        assert result["status"] == "partial"

    def test_no_dob_skips_age_check(self):
        profile = {"category": "General"}
        notification = {"min_age": 21, "max_age": 32}
        result = check_eligibility(profile, notification)
        # No age check performed, no failure
        assert result["status"] == "eligible"


class TestEligibilityEducation:
    """Test education-based eligibility checking."""

    def test_sufficient_education(self):
        profile = {"education_level": "Graduation"}
        notification = {"education_required": "12th"}
        result = check_eligibility(profile, notification)
        assert result["status"] == "eligible"
        assert any("✓" in r for r in result["reasons"])

    def test_exact_education(self):
        profile = {"education_level": "Graduation"}
        notification = {"education_required": "Graduation"}
        result = check_eligibility(profile, notification)
        assert result["status"] == "eligible"

    def test_insufficient_education(self):
        profile = {"education_level": "12th"}
        notification = {"education_required": "Graduation"}
        result = check_eligibility(profile, notification)
        assert result["status"] == "not_eligible"
        assert any("Requires" in r for r in result["reasons"])

    def test_phd_qualifies_for_all(self):
        profile = {"education_level": "PhD"}
        notification = {"education_required": "Graduation"}
        result = check_eligibility(profile, notification)
        assert result["status"] == "eligible"

    def test_no_education_skips_check(self):
        profile = {}
        notification = {"education_required": "Graduation"}
        result = check_eligibility(profile, notification)
        assert result["status"] == "eligible"


class TestEligibilityCategory:
    """Test category vacancy checking."""

    def test_category_has_vacancies(self):
        profile = {"category": "OBC"}
        notification = {
            "vacancy_by_category": {"General": 100, "OBC": 50, "SC": 30},
        }
        result = check_eligibility(profile, notification)
        assert result["status"] == "eligible"
        assert any("50 vacancies" in r for r in result["reasons"])

    def test_category_zero_vacancies(self):
        profile = {"category": "ST"}
        notification = {
            "vacancy_by_category": {"General": 100, "OBC": 50, "ST": 0},
        }
        result = check_eligibility(profile, notification)
        assert result["status"] == "partial"
        assert any("No vacancies" in r for r in result["reasons"])


class TestEligibilityState:
    """Test state-specific eligibility (State PSC exams)."""

    def test_matching_state(self):
        profile = {"state": "Bihar"}
        notification = {"organization": "BPSC", "exam_type": "State"}
        result = check_eligibility(profile, notification)
        assert result["status"] == "eligible"
        assert any("State Bihar ✓" in r for r in result["reasons"])

    def test_wrong_state(self):
        profile = {"state": "Maharashtra"}
        notification = {"organization": "BPSC", "exam_type": "State"}
        result = check_eligibility(profile, notification)
        assert result["status"] == "not_eligible"
        assert any("Requires Bihar" in r for r in result["reasons"])

    def test_no_state_set(self):
        profile = {}
        notification = {"organization": "UPPSC", "exam_type": "State"}
        result = check_eligibility(profile, notification)
        assert result["status"] == "partial"
        assert any("update your state" in r for r in result["reasons"])

    def test_central_exam_ignores_state(self):
        profile = {"state": "Bihar"}
        notification = {"organization": "UPSC", "exam_type": "Central"}
        result = check_eligibility(profile, notification)
        # Central exams don't check state
        assert result["status"] == "eligible"


class TestEligibilityCombined:
    """Test combined eligibility checks."""

    def test_fully_eligible_candidate(self):
        profile = {
            "dob": "2000-01-01",
            "category": "General",
            "education_level": "Graduation",
            "state": "Bihar",
        }
        notification = {
            "min_age": 21,
            "max_age": 32,
            "education_required": "Graduation",
            "organization": "SSC",
            "exam_type": "Central",
            "vacancy_by_category": {"General": 500},
        }
        result = check_eligibility(profile, notification)
        assert result["status"] == "eligible"

    def test_multiple_failures(self):
        profile = {
            "dob": "1980-01-01",  # too old
            "category": "General",
            "education_level": "10th",  # too low
        }
        notification = {
            "min_age": 21,
            "max_age": 32,
            "education_required": "Graduation",
        }
        result = check_eligibility(profile, notification)
        assert result["status"] == "not_eligible"
        assert len(result["reasons"]) >= 2

    def test_empty_profile(self):
        """Empty profile should not crash."""
        result = check_eligibility({}, {})
        assert result["status"] == "eligible"
        assert isinstance(result["reasons"], list)

    def test_empty_notification(self):
        """Empty notification should not crash."""
        profile = {
            "dob": "2000-01-01",
            "category": "General",
            "education_level": "Graduation",
        }
        result = check_eligibility(profile, {})
        assert result["status"] == "eligible"
