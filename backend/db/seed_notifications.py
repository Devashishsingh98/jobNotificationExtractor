"""Seed sample government job notifications for demo/testing."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import get_db

SAMPLE_NOTIFICATIONS = [
    {
        "title": "UPSC Civil Services Examination 2026",
        "organization": "UPSC",
        "exam_type": "Central",
        "last_date": "2026-04-15",
        "min_age": 21,
        "max_age": 32,
        "age_relaxation": {"OBC": 3, "SC": 5, "ST": 5},
        "education_required": "Graduate",
        "total_vacancies": 1056,
        "vacancy_by_category": {"General": 400, "OBC": 280, "SC": 160, "ST": 80, "EWS": 136},
        "original_pdf_url": "https://upsc.gov.in/sites/default/files/Notif-CSE-26-engl.pdf",
        "official_website_url": "https://upsc.gov.in",
        "source_channel": "demo_seed",
        "source_message_id": 1001,
        "raw_text": "UPSC Civil Services Examination 2026 notification",
        "is_processed": True,
    },
    {
        "title": "SSC CGL Tier-I Examination 2026",
        "organization": "SSC",
        "exam_type": "Central",
        "last_date": "2026-05-01",
        "min_age": 18,
        "max_age": 32,
        "age_relaxation": {"OBC": 3, "SC": 5, "ST": 5},
        "education_required": "Graduate",
        "total_vacancies": 14582,
        "vacancy_by_category": {"General": 5500, "OBC": 3900, "SC": 2200, "ST": 1100, "EWS": 1882},
        "original_pdf_url": "https://ssc.nic.in/SSCFileServer/PortalManagement/UploadedFiles/notice_cgl2026.pdf",
        "official_website_url": "https://ssc.nic.in",
        "source_channel": "demo_seed",
        "source_message_id": 1002,
        "raw_text": "SSC CGL 2026 recruitment notification",
        "is_processed": True,
    },
    {
        "title": "IBPS PO/MT-XIV Recruitment 2026",
        "organization": "IBPS",
        "exam_type": "Banking",
        "last_date": "2026-04-20",
        "min_age": 20,
        "max_age": 30,
        "age_relaxation": {"OBC": 3, "SC": 5, "ST": 5},
        "education_required": "Graduate",
        "total_vacancies": 4455,
        "vacancy_by_category": {"General": 1780, "OBC": 1200, "SC": 670, "ST": 350, "EWS": 455},
        "original_pdf_url": "https://ibps.in/wp-content/uploads/CRP_PO_MT_XIV.pdf",
        "official_website_url": "https://ibps.in",
        "source_channel": "demo_seed",
        "source_message_id": 1003,
        "raw_text": "IBPS PO recruitment 2026",
        "is_processed": True,
    },
    {
        "title": "RRB NTPC Graduate Level Recruitment 2026",
        "organization": "RRB",
        "exam_type": "Railway",
        "last_date": "2026-05-15",
        "min_age": 18,
        "max_age": 33,
        "age_relaxation": {"OBC": 3, "SC": 5, "ST": 5},
        "education_required": "Graduate",
        "total_vacancies": 11558,
        "vacancy_by_category": {"General": 4600, "OBC": 3100, "SC": 1730, "ST": 870, "EWS": 1258},
        "original_pdf_url": "https://www.rrbcdg.gov.in/uploads/NTPC2026.pdf",
        "official_website_url": "https://www.rrbcdg.gov.in",
        "source_channel": "demo_seed",
        "source_message_id": 1004,
        "raw_text": "RRB NTPC 2026 recruitment",
        "is_processed": True,
    },
    {
        "title": "BPSC 70th Combined Competitive Examination",
        "organization": "BPSC",
        "exam_type": "State",
        "last_date": "2026-04-30",
        "min_age": 20,
        "max_age": 37,
        "age_relaxation": {"OBC": 3, "SC": 5, "ST": 5},
        "education_required": "Graduate",
        "total_vacancies": 1929,
        "vacancy_by_category": {"General": 580, "OBC": 520, "SC": 310, "ST": 100, "EWS": 419},
        "original_pdf_url": "https://www.bpsc.bih.nic.in/Advt/70th_CCE.pdf",
        "official_website_url": "https://www.bpsc.bih.nic.in",
        "source_channel": "demo_seed",
        "source_message_id": 1005,
        "raw_text": "BPSC 70th CCE notification",
        "is_processed": True,
    },
    {
        "title": "UPPSC PCS Pre Examination 2026",
        "organization": "UPPSC",
        "exam_type": "State",
        "last_date": "2026-05-10",
        "min_age": 21,
        "max_age": 40,
        "age_relaxation": {"OBC": 3, "SC": 5, "ST": 5},
        "education_required": "Graduate",
        "total_vacancies": 630,
        "vacancy_by_category": {"General": 200, "OBC": 170, "SC": 130, "ST": 40, "EWS": 90},
        "original_pdf_url": "https://uppsc.up.nic.in/CandidatePages/Notifications/PCS2026.pdf",
        "official_website_url": "https://uppsc.up.nic.in",
        "source_channel": "demo_seed",
        "source_message_id": 1006,
        "raw_text": "UPPSC PCS 2026 notification",
        "is_processed": True,
    },
    {
        "title": "Indian Navy Agniveer SSR/MR 02/2026 Batch",
        "organization": "Indian Navy",
        "exam_type": "Defence",
        "last_date": "2026-04-10",
        "min_age": 17,
        "max_age": 21,
        "education_required": "12th",
        "total_vacancies": 2800,
        "original_pdf_url": "https://www.joinindiannavy.gov.in/uploads/agniveer_ssr_mr_02_2026.pdf",
        "official_website_url": "https://www.joinindiannavy.gov.in",
        "source_channel": "demo_seed",
        "source_message_id": 1007,
        "raw_text": "Indian Navy Agniveer recruitment 2026",
        "is_processed": True,
    },
    {
        "title": "NTPC Limited Engineering Executive Trainee 2026",
        "organization": "NTPC",
        "exam_type": "PSU",
        "last_date": "2026-04-25",
        "min_age": 21,
        "max_age": 30,
        "age_relaxation": {"OBC": 3, "SC": 5, "ST": 5},
        "education_required": "B.Tech/B.E.",
        "total_vacancies": 864,
        "vacancy_by_category": {"General": 345, "OBC": 230, "SC": 130, "ST": 65, "EWS": 94},
        "original_pdf_url": "https://www.ntpc.co.in/career/files/ET2026.pdf",
        "official_website_url": "https://www.ntpc.co.in",
        "source_channel": "demo_seed",
        "source_message_id": 1008,
        "raw_text": "NTPC Engineering Executive Trainee 2026",
        "is_processed": True,
    },
    {
        "title": "SSC CHSL (10+2) Level Examination 2026",
        "organization": "SSC",
        "exam_type": "Central",
        "last_date": "2026-05-20",
        "min_age": 18,
        "max_age": 27,
        "age_relaxation": {"OBC": 3, "SC": 5, "ST": 5},
        "education_required": "12th",
        "total_vacancies": 6850,
        "vacancy_by_category": {"General": 2740, "OBC": 1850, "SC": 1030, "ST": 520, "EWS": 710},
        "original_pdf_url": "https://ssc.nic.in/SSCFileServer/PortalManagement/UploadedFiles/notice_chsl2026.pdf",
        "official_website_url": "https://ssc.nic.in",
        "source_channel": "demo_seed",
        "source_message_id": 1009,
        "raw_text": "SSC CHSL 2026 recruitment",
        "is_processed": True,
    },
    {
        "title": "SBI Clerk Junior Associate Recruitment 2026",
        "organization": "SBI",
        "exam_type": "Banking",
        "last_date": "2026-04-05",
        "min_age": 20,
        "max_age": 28,
        "age_relaxation": {"OBC": 3, "SC": 5, "ST": 5},
        "education_required": "Graduate",
        "total_vacancies": 8773,
        "vacancy_by_category": {"General": 3510, "OBC": 2370, "SC": 1320, "ST": 660, "EWS": 913},
        "original_pdf_url": "https://sbi.co.in/documents/clerk2026.pdf",
        "official_website_url": "https://sbi.co.in/web/careers",
        "source_channel": "demo_seed",
        "source_message_id": 1010,
        "raw_text": "SBI Clerk 2026 recruitment",
        "is_processed": True,
    },
]


def seed():
    db = get_db()

    # Check if seed data already exists
    existing = db.table("notifications").select("id").eq("source_channel", "demo_seed").execute()
    if existing.data:
        print(f"Seed data already exists ({len(existing.data)} notifications). Skipping.")
        return

    for notif in SAMPLE_NOTIFICATIONS:
        try:
            db.table("notifications").insert(notif).execute()
            print(f"  Seeded: {notif['title']}")
        except Exception as e:
            print(f"  Error seeding {notif['title']}: {e}")

    print(f"\nDone! Seeded {len(SAMPLE_NOTIFICATIONS)} sample notifications.")


if __name__ == "__main__":
    seed()
