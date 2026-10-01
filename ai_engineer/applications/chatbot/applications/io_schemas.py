from pydantic import BaseModel

class LLMResponseOutput(BaseModel):
    content: str

class QueryUnderstandOutput(BaseModel):
    """
        QueryUnderstandOutput is a response from LLM.
        
        LLM will understand the query and return the response in this format.

        {
            'original_query': 'Loi nhuan cua ngan hang ACB ngay 10 thang 9', 
            'vietnamese_with_diacritics': 'Lợi nhuận của ngân hàng ACB ngày 10 tháng 9', 
            'question_type': 'tài chính doanh nghiệp', 
            'main_topic': 'Tài chính Doanh nghiệp', 
            'stock_id': 'ACB', 'target_year': '2026', 
            'document_type': 'income_statement', 
            'optimized_search_query': 
                [
                    'báo cáo lợi nhuận ngân hàng ACB năm 2026', 
                    'tình hình tài chính và lợi nhuận ACB mới nhất', 
                    'số liệu doanh thu lợi nhuận ngân hàng ACB năm 2026'
                ]
        }
    """
    original_query: str
    vietnamese_with_diacritics: str
    question_type: str
    main_topic: str
    stock_id: str
    target_year: str
    document_type: str
    optimized_search_query: list[str]