import polars as pl
from unidecode import unidecode

from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter

# qdrant_extractor = QdrantExtractorWithPayloadFilter(
#     qdrant_url="http://localhost:6333",
#     collection_name="newspaper",
#     payload_filter={
#         "publish_date": "2026-06-25",
#     },
# )

# df = qdrant_extractor.extract(
    
# )

# df = df.select([
#     "id",
#     "stock_mention",
#     "topic_keywords",
#     "sentiment_analysis",
#     "mention_people",
#     "mention_stock_funds",
#     "foreign_securities_funds",
#     "government_policies",
#     "topic_tagging",
# ])

def normalize_value(value):
    if isinstance(value, str):
        return unidecode(value)
    if isinstance(value, list):
        return [unidecode(item).lower() if isinstance(item, str) else item for item in value]
    return value

# df = 1. Tạo một DataFrame tiếng Việt mẫu
dict_ = {'id': '0060ec7a85c245d3a6a56234fe18eae5', 'topic_keywords': ['cho vay lãi nặng', 'tín dụng đen', 'ATM Online', 'Công ty TM 24H', 'lãi suất'], 'stock_mention': [], 'mention_people': ['Đỗ Minh Hải', 'Verevkin Vladimir', 'Alexey Bychkov', 'Sergey Lykosov', 'Trần Đình Triển', 'Nguyễn Thị Thúy Diễm', 'Đỗ Thị Minh Hiếu', 'Nguyễn Thanh Sang', 'Phạm Thị Ngọc Bích'], 'mention_stock_funds': [], 'foreign_securities_funds': [], 'government_policies': []}


dict_khong_dau = {
    key: value if key == "id" else normalize_value(value)
    for key, value in dict_.items()
}

print(dict_khong_dau)