from pydantic import BaseModel


class InputVectorSearch(BaseModel):
    query: str
    

class OutputVectorSearch(BaseModel):
    results: list[dict]
