from pydantic import BaseModel, Field
from typing import Optional, List

class KeywordSpec(BaseModel):
    text: str
    match_type: str = "EXACT"  # BROAD, PHRASE, EXACT

class ResponsiveSearchAdSpec(BaseModel):
    headlines: List[str]
    descriptions: List[str]
    final_url: str

class AdGroupSpec(BaseModel):
    name: str
    max_cpc_usd: float = 1.0
    ad: Optional[ResponsiveSearchAdSpec] = None
    keywords: List[KeywordSpec] = Field(default_factory=list)
    negative_keywords: List[str] = Field(default_factory=list)

class CampaignSpec(BaseModel):
    name: str
    channel: str = "SEARCH"
    daily_budget_usd: float
    status: str = "PAUSED"
    target_country: Optional[str] = "United States"
    target_language: Optional[str] = "English"
    bidding_strategy: str = "MANUAL_CPC"
    ad_groups: List[AdGroupSpec] = Field(default_factory=list)

class CampaignCreate(BaseModel):
    name: str
    budget_amount_micros: int
    advertising_channel_type: str = "SEARCH"
    status: str = "PAUSED"

class CampaignBudgetCreate(BaseModel):
    name: str
    amount_micros: int

class CampaignInfo(BaseModel):
    id: str
    name: str
    status: str
    advertising_channel_type: str
    budget_id: Optional[str] = None
    budget_amount_micros: Optional[int] = None
