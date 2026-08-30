from typing import Literal
from pydantic import BaseModel, ConfigDict, RootModel, field_validator

# Business analysis 
class BusinessNewspaperSummary(BaseModel):
    summary: str 
    sentiment_analysis: Literal["Tích cực", "Tiêu cực", "Trung lập"] 

class BusinessNewspaperSummaryOutput(RootModel[dict[str, BusinessNewspaperSummary]]):
    pass

# Macro summary
class MacroNewspaperSummary(BaseModel):
    summary: str
    sentiment_analysis: Literal["Tích cực", "Tiêu cực", "Trung lập"] 
    circular_and_policy: list[str]
    
class MacroNewspaperSummaryOutput(RootModel[dict[str, MacroNewspaperSummary]]):
    pass

# Market summary
class MarketNewspaperSummary(BaseModel):
    summary: str
    sentiment_analysis: Literal["Tích cực", "Tiêu cực", "Trung lập"] 
    circular_and_policy: list[str]
    
class MarketNewspaperSummaryOutput(RootModel[dict[str, MarketNewspaperSummary]]):
    pass

# Fund summary
class FundNewspaperSummary(BaseModel):
    summary: str
    sentiment_analysis: Literal["Tích cực", "Tiêu cực", "Trung lập"] 
    fund_name: list[str]
    
class FundNewspaperSummaryOutput(RootModel[dict[str, FundNewspaperSummary]]):
    pass

# Law summary
class LawNewspaperSummary(BaseModel):
    summary: str
    sentiment_analysis: Literal["Tích cực", "Tiêu cực", "Trung lập"] 
    legal_documents_and_regulations: list[str]
    
class LawNewspaperSummaryOutput(RootModel[dict[str, LawNewspaperSummary]]):
    pass