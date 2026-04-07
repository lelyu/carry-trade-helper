from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
from uuid import UUID


class PreferencesBase(BaseModel):
    currency_pairs: List[str]
    email_frequency: str = "daily"
    alert_thresholds: Dict[str, Any] | None = None
    is_active: bool = True


class PreferencesCreate(PreferencesBase):
    pass


class PreferencesUpdate(BaseModel):
    currency_pairs: List[str] | None = None
    email_frequency: str | None = None
    alert_thresholds: Dict[str, Any] | None = None
    is_active: bool | None = None


class PreferencesResponse(PreferencesBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True