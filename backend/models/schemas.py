from pydantic import BaseModel
from datetime import date


class PassportData(BaseModel):
    passport_number: str | None = None
    surname: str | None = None
    given_names: str | None = None
    nationality: str | None = None
    date_of_birth: str | None = None
    sex: str | None = None
    place_of_birth: str | None = None
    date_of_issue: str | None = None
    date_of_expiry: str | None = None
    issuing_authority: str | None = None
    mrz_line1: str | None = None
    mrz_line2: str | None = None
    raw_ocr_text: str | None = None


class ClientProfile(BaseModel):
    client_id: str
    phone: str | None = None
    email: str | None = None
    full_name: str | None = None
    preferred_language: str = "fr"
    profile_type: str = "unknown"
    budget_preference: str = "unknown"


class ProgramInfo(BaseModel):
    id: int
    title_fr: str
    title_ar: str | None = None
    destination: str
    description_fr: str | None = None
    description_ar: str | None = None
    duration_days: int | None = None
    price: float | None = None
    currency: str = "TND"
    category: str | None = None
    target_audience: str | None = None
    includes: list[str] = []
    hotel_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class Recommendation(BaseModel):
    program: ProgramInfo
    score: float
    reason: str
