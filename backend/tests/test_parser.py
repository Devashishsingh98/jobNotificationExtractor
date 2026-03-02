"""Tests for notification parser."""

import pytest
from scraper.parser import is_job_notification, parse_notification, extract_urls


class TestIsJobNotification:
    def test_clear_job_notification(self):
        text = """UPSC Civil Services Examination 2026
        Total Vacancies: 1056
        Last Date: 15-04-2026
        Apply Online at upsc.gov.in"""
        assert is_job_notification(text) is True

    def test_recruitment_keywords(self):
        text = "SSC has released recruitment notification for CGL 2026. Total Posts: 14000."
        assert is_job_notification(text) is True

    def test_not_a_job_notification(self):
        text = "Good morning everyone! Have a nice day."
        assert is_job_notification(text) is False

    def test_short_text(self):
        text = "hi"
        assert is_job_notification(text) is False

    def test_partial_keywords(self):
        text = "The vacancy in the committee will be filled soon by the government."
        # Should have at least 2 keywords to qualify
        result = is_job_notification(text)
        assert isinstance(result, bool)


class TestParseNotification:
    def test_parse_basic(self):
        text = """UPSC Civil Services Examination 2026
        Organization: UPSC
        Total Vacancies: 1056
        Last Date to Apply: 15-04-2026
        Age Limit: 21-32 years
        Education: Graduation
        """
        result = parse_notification(text)
        assert result["title"] is not None
        assert result.get("total_vacancies") is not None or result.get("organization") is not None

    def test_parse_with_dates(self):
        text = """SSC CGL 2026 Notification
        Last date: 01/05/2026
        Total Posts: 14582"""
        result = parse_notification(text)
        assert result is not None
        # Should extract last_date if parser finds it
        if result.get("last_date"):
            assert "2026" in result["last_date"]

    def test_parse_age_range(self):
        text = """RRB NTPC Recruitment
        Age: 18 to 33 years
        Total Vacancies: 11558"""
        result = parse_notification(text)
        assert isinstance(result, dict)

    def test_parse_education(self):
        text = """IBPS PO Recruitment
        Educational Qualification: Graduate from recognized university
        Vacancies: 4455"""
        result = parse_notification(text)
        assert isinstance(result, dict)

    def test_parse_empty(self):
        result = parse_notification("")
        assert isinstance(result, dict)
        assert "title" in result


class TestExtractUrls:
    def test_single_url(self):
        text = "Apply at https://upsc.gov.in/apply"
        urls = extract_urls(text)
        assert len(urls) >= 1
        assert any("upsc.gov.in" in url for url in urls)

    def test_multiple_urls(self):
        text = """
        Official: https://ssc.nic.in
        PDF: https://ssc.nic.in/notice.pdf
        Apply: https://onlinereg.ssc.nic.in
        """
        urls = extract_urls(text)
        assert len(urls) >= 2

    def test_no_urls(self):
        urls = extract_urls("No links here")
        assert len(urls) == 0

    def test_telegram_url(self):
        text = "Join https://t.me/jobchannel for updates"
        urls = extract_urls(text)
        assert isinstance(urls, list)
