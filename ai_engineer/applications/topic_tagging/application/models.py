from pydantic import BaseModel, ConfigDict, field_validator
from typing import List



class TopicTagging(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    main_topic: List[str]
    stocks_mention: List[str]
    person_mention: List[str]

    @field_validator(
        "main_topic",
        "stocks_mention",
        "person_mention",
        mode="before",
    )
    @classmethod
    def _normalize_string_list(cls, v):
        null_tokens = {"none", "null", "nan", ""}

        if v is None:
            return []

        if isinstance(v, str):
            s = v.strip()
            if s.lower() in null_tokens:
                return []
            parts = [p.strip() for p in s.split(",")]
            return [p for p in parts if p and p.lower() not in null_tokens]

        if isinstance(v, list):
            out: list[str] = []
            for item in v:
                if item is None:
                    continue
                s = item.strip() if isinstance(item, str) else str(item).strip()
                if not s or s.lower() in null_tokens:
                    continue
                out.append(s)
            return out

        return v


class TopicTaggingDAB(BaseModel):
    model_config = ConfigDict(extra="forbid")

    newspaper_url: str
    main_topic: List[str]
    stocks_mention: List[str]
    person_mention: List[str]
    newspaper_summary: str
    sentiment_analysis: str

    @field_validator(
        "main_topic",
        "stocks_mention",
        "person_mention",
        mode="before",
    )
    @classmethod
    def _normalize_string_list(cls, v):
        null_tokens = {"none", "null", "nan", ""}

        if v is None:
            return []

        if isinstance(v, str):
            s = v.strip()
            if s.lower() in null_tokens:
                return []
            parts = [p.strip() for p in s.split(",")]
            return [p for p in parts if p and p.lower() not in null_tokens]

        if isinstance(v, list):
            out: list[str] = []
            for item in v:
                if item is None:
                    continue
                s = item.strip() if isinstance(item, str) else str(item).strip()
                if not s or s.lower() in null_tokens:
                    continue
                out.append(s)
            return out

        return v

    @field_validator("newspaper_summary", mode="before")
    @classmethod
    def _normalize_summary(cls, v):
        # LLM đôi khi trả về list cho summary dù schema yêu cầu string.
        # Coerce về string để tránh lỗi validation.
        if v is None:
            return ""
        if isinstance(v, list):
            return "\n".join(
                str(item).strip()
                for item in v
                if item is not None and str(item).strip()
            )
        if isinstance(v, str):
            return v
        return str(v)