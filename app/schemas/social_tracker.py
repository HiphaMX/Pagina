import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class SocialSnapshotResponse(BaseModel):
    id: int
    account_id: int
    followers: int
    growth_count: Optional[int] = 0
    is_manual: bool = False
    recorded_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class SocialAccountCreate(BaseModel):
    url: str
    client_id: Optional[int] = None
    name: Optional[str] = None
    notes: Optional[str] = None
    initial_followers: Optional[int] = None


class SocialAccountUpdate(BaseModel):
    name: Optional[str] = None
    client_id: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class ManualSnapshotCreate(BaseModel):
    followers: int
    recorded_at: Optional[datetime.datetime] = None


class SocialAccountResponse(BaseModel):
    id: int
    client_id: Optional[int] = None
    client_name: Optional[str] = None
    platform: str
    name: str
    handle: Optional[str] = None
    url: str
    avatar_url: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime.datetime
    current_followers: int = 0
    initial_followers: int = 0
    growth_total: int = 0
    growth_monthly: int = 0
    growth_percentage: float = 0.0
    last_scanned_at: Optional[datetime.datetime] = None
    sparkline_history: List[int] = []
    snapshots: List[SocialSnapshotResponse] = []

    model_config = ConfigDict(from_attributes=True)


class SocialObservatoryOverview(BaseModel):
    total_accounts: int
    total_audience: int
    total_monthly_growth: int
    instagram_accounts: int
    facebook_accounts: int
    accounts: List[SocialAccountResponse]
