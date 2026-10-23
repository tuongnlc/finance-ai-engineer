import polars as pl
import streamlit as st
from datetime import date, timedelta
from ai_engineer.frontend.applications.market_info.services.newspaper_summary.newspaper_summary_service import NewspaperSummaryService
from ai_engineer.frontend.components.filter.date_filter import DateFilter
from ai_engineer.frontend.components.markdown.markdown import MarkDown
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from ai_engineer.frontend.components.filter.multi_select_dropdown_filter import MultiSelectDropdownFilter


QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "newspaper_summary"


def _unique_options(df: pl.DataFrame, column: str) -> list:
    """Lấy danh sách giá trị duy nhất của một cột."""
    if df.is_empty() or column not in df.columns:
        return []
    return df[column].unique().drop_nulls().sort().to_list()


def _filter_by_values(df: pl.DataFrame, column: str, selected: list) -> pl.DataFrame:
    """Giữ các dòng có giá trị nằm trong `selected`."""
    if not selected:
        return df.head(0)
    return df.filter(pl.col(column).is_in(selected))


def market_news():
    st.set_page_config(
        page_title="Market News",
        layout="wide"  
    )

    # Hiển thị popup sau khi rerun
    toast_message = st.session_state.pop("favorite_toast", None)
    if toast_message:
        st.toast(toast_message, icon="✅")

    # Prepare filters
    col_left, col_right = st.columns([2, 1])
    max_date = date.today()
    min_date = max_date - timedelta(days=90)
    with col_left:
        input_date_filter = DateFilter(
            min_date=min_date, max_date=max_date
        )
        start_date, end_date = input_date_filter.render()

    summaries = NewspaperSummaryService().list_summaries(start_date, end_date)
    news = pl.DataFrame(
        [
            {
                "summary_id": str(item.summary_id),
                "publish_date": item.publish_date,
                "news_type": item.newspaper_type,
                "news_summary": item.newspaper_summary,
                "sentiment_analysis": item.sentiment_analysis,
                "main_topic": item.main_topic,
                "stocks_mention": item.stocks_mention,
                "fund_name": item.fund_name,
                "circular_and_policy": item.circular_and_policy,
                "legal_documents_and_regulations": item.legal_documents_and_regulations,
                "is_favorite": item.is_favorite,
            }
            for item in summaries
        ],
        schema={
            "summary_id": pl.Utf8,
            "publish_date": pl.Date,
            "news_type": pl.Utf8,
            "news_summary": pl.Utf8,
            "sentiment_analysis": pl.Utf8,
            "main_topic": pl.Utf8,
            "stocks_mention": pl.Utf8,
            "fund_name": pl.Utf8,
            "circular_and_policy": pl.Utf8,
            "legal_documents_and_regulations": pl.Utf8,
            "is_favorite": pl.Int8,
        },
    ).sort("publish_date", descending=True).filter(pl.col("is_favorite") == 1)

    # Các filter liên tiếp: options của filter sau dựa trên kết quả của filter trước
    cascading_filters = [
        ("Công ty liên quan", "stocks_mention"),
        ("Trạng thái", "sentiment_analysis"),
        ("Chủ đề", "main_topic"),
    ]
    filter_cols = st.columns(len(cascading_filters))
    for (filter_name, column), filter_col in zip(cascading_filters, filter_cols):
        with filter_col:
            selected_values = MultiSelectDropdownFilter(
                filter_name=filter_name,
                options=_unique_options(news, column),
            ).render()
        news = _filter_by_values(news, column, selected_values)

    st.divider()

    MarkDown(
        font_size="28px",    
        text="TIN TỨC THỊ TRƯỜNG"
    ).render()
    st.write(f"Xem tin tức thị trường đáng chú ý ngày: {start_date} đến {end_date}")

    news = news.to_dicts()
    for idx, conv in enumerate(news):
        with st.container(border=True):
            #f":blue[{publish_date}]"
            publish_date = conv.get("publish_date")
            stocks_mention = conv.get("stocks_mention")
            news_type = conv.get("news_type")
            sentiment_analysis = conv.get("sentiment_analysis")
            circular_and_policy = conv.get("circular_and_policy")
            legal_documents_and_regulations = conv.get("legal_documents_and_regulations")
            fund_name = conv.get("fund_name")
            # sensi
            st.caption(f":blue[Ngày đăng: {publish_date} - Trạng thái: {sentiment_analysis}]")

            st.caption(f":blue[Loại tin tức: {news_type}]")

            news_summary = conv.get("news_summary")
            
            st.write(news_summary)

            if stocks_mention:
                st.caption(f":green[Chứng khoán liên quan: {stocks_mention}]")
            if fund_name:
                st.caption(f":green[Quỹ liên quan: {fund_name}]")

            if circular_and_policy:
                st.caption(f":red[Thông tư và chính sách liên quan: {circular_and_policy}]")
            if legal_documents_and_regulations:
                st.caption(f":red[Văn bản pháp luật liên quan: {legal_documents_and_regulations}]")  

            


if __name__ == "__main__":
    market_news()
