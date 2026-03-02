"""Pydantic schemas for request/response models."""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import date, datetime


# ---- Auth ----

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    telegram_username: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str


# ---- User Profile ----

class UserProfileCreate(BaseModel):
    dob: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(M|F|Other)$")
    education_level: Optional[str] = Field(None, pattern="^(10th|12th|Diploma|Graduation|Post Graduation|PhD)$")
    education_stream: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, pattern="^(General|OBC|SC|ST|EWS)$")
    state: Optional[str] = Field(None, max_length=100)
    exam_interests: list[str] = Field(default_factory=list, max_length=20)

    @field_validator('dob')
    @classmethod
    def validate_dob(cls, v):
        if v:
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 18:
                raise ValueError("Must be at least 18 years old")
            if age > 100:
                raise ValueError("Invalid date of birth")
        return v

    @field_validator('exam_interests')
    @classmethod
    def validate_exam_interests(cls, v):
        if v:
            allowed = ["Central", "State", "Banking", "Railway", "Defence", "PSU"]
            for interest in v:
                if interest not in allowed:
                    raise ValueError(f"Invalid exam interest: {interest}")
        return v


class UserProfileResponse(BaseModel):
    user_id: str
    dob: Optional[date] = None
    gender: Optional[str] = None
    education_level: Optional[str] = None
    education_stream: Optional[str] = None
    category: Optional[str] = None
    state: Optional[str] = None
    exam_interests: list[str] = []


class UserResponse(BaseModel):
    id: str
    email: str
    telegram_username: Optional[str] = None
    telegram_chat_id: Optional[int] = None
    is_premium: bool = False
    role: str = "user"
    created_at: Optional[datetime] = None


# ---- Notifications ----

class NotificationResponse(BaseModel):
    id: int
    title: str
    organization: Optional[str] = None
    exam_type: Optional[str] = None
    original_pdf_url: Optional[str] = None
    official_website_url: Optional[str] = None
    last_date: Optional[date] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    age_relaxation: dict = {}
    education_required: Optional[str] = None
    total_vacancies: Optional[int] = None
    vacancy_by_category: dict = {}
    source_channel: Optional[str] = None
    is_processed: bool = False
    created_at: Optional[datetime] = None
    # Added by eligibility engine
    eligibility_status: Optional[str] = None
    eligibility_reasons: list[str] = []


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    total: int
    page: int
    per_page: int


# ---- Selections ----

class SelectionCreate(BaseModel):
    notification_ids: list[int] = Field(min_length=1, max_length=50)

    @field_validator('notification_ids')
    @classmethod
    def validate_notification_ids(cls, v):
        if v:
            if len(v) != len(set(v)):
                raise ValueError("Duplicate notification IDs found")
            for nid in v:
                if nid <= 0:
                    raise ValueError(f"Invalid notification ID: {nid}")
        return v


# ---- Channels ----

class ChannelCreate(BaseModel):
    channel_username: str = Field(min_length=3, max_length=100)
    channel_name: Optional[str] = Field(None, max_length=200)

    @field_validator('channel_username')
    @classmethod
    def validate_channel_username(cls, v):
        if v:
            # Remove @ prefix if present
            clean = v.lstrip('@')
            # Validate telegram username format (alphanumeric and underscore)
            if not clean.replace('_', '').isalnum():
                raise ValueError("Invalid Telegram username format")
            return clean
        return v


class ChannelResponse(BaseModel):
    id: int
    channel_username: str
    channel_name: Optional[str] = None
    is_active: bool = True
    last_scraped_id: int = 0


# ---- User Preferences ----

VALID_EXAM_TYPES = ["Central", "State", "Banking", "Railway", "Defence", "PSU"]
VALID_ORGS = [
    "UPSC", "SSC", "IBPS", "RBI", "RRB", "NTA", "DRDO", "ISRO",
    "BPSC", "UPPSC", "MPPSC", "RPSC", "WBPSC", "KPSC", "TNPSC",
    "APPSC", "TSPSC", "HPPSC", "UKPSC", "CGPSC", "JPSC", "GPSC", "MPSC",
    "SBI", "NABARD", "LIC", "EPFO", "FCI", "SAIL", "ONGC", "NTPC", "AAI",
]


class UserPreferencesCreate(BaseModel):
    preferred_exam_types: list[str] = Field(default_factory=list)
    preferred_states: list[str] = Field(default_factory=list)
    preferred_orgs: list[str] = Field(default_factory=list)
    min_education: Optional[str] = Field(None, pattern="^(10th|12th|Diploma|Graduation|Post Graduation|PhD)$")
    notify_via: list[str] = Field(default_factory=lambda: ["website"])
    max_notifications_per_day: int = Field(10, ge=1, le=50)

    @field_validator('preferred_exam_types')
    @classmethod
    def validate_exam_types(cls, v):
        for t in v:
            if t not in VALID_EXAM_TYPES:
                raise ValueError(f"Invalid exam type: {t}")
        return v

    @field_validator('notify_via')
    @classmethod
    def validate_notify_via(cls, v):
        allowed = ["website", "telegram"]
        for ch in v:
            if ch not in allowed:
                raise ValueError(f"Invalid notify channel: {ch}")
        return v


class UserPreferencesResponse(BaseModel):
    user_id: Optional[str] = None
    preferred_exam_types: list[str] = []
    preferred_states: list[str] = []
    preferred_orgs: list[str] = []
    min_education: Optional[str] = None
    notify_via: list[str] = ["website"]
    max_notifications_per_day: int = 10

