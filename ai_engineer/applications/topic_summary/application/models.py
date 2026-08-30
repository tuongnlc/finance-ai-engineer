from typing import Literal
from pydantic import BaseModel, ConfigDict, RootModel, field_validator


class TopicAnalysis(BaseModel):
    summary: str 
    sentiment_analysis: Literal["Tích cực", "Tiêu cực", "Trung lập"] 

class TopicAnalysisOutput(RootModel[dict[str, TopicAnalysis]]):
    pass



class MacroNewspaperSummary(BaseModel):
    summary: str
    sentiment_analysis: Literal["Tích cực", "Tiêu cực", "Trung lập"] 
    circular_and_policy: list[str]
    
class MacroNewspaperSummaryOutput(RootModel[dict[str, MacroNewspaperSummary]]):
    pass