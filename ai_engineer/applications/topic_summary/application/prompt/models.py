from typing import Literal
from pydantic import BaseModel, ConfigDict, RootModel, field_validator


class TopicAnalysis(BaseModel):
    summary: str 
    sentiment_analysis: Literal["Tích cực", "Tiêu cực", "Trung lập"] 

class TopicAnalysisOutput(RootModel[dict[str, TopicAnalysis]]):
    pass