# from polars import date
import streamlit as st
from datetime import date, timedelta
from ai_engineer.frontend.components.filter.date_filter import DateFilter
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter
from ai_engineer.frontend.components.filter.multi_select_dropdown_filter import MultiSelectDropdownFilter


def market_news():
    st.set_page_config(
        page_title="Market News",
        layout="wide"  
    )

    # Prepare filters
    col_left, col_right = st.columns([2, 1])
    max_date = date.today()
    min_date = max_date - timedelta(days=90)
    with col_left:
        input_date_filter = DateFilter(
            min_date=min_date, max_date=max_date
        )
        start_date, end_date = input_date_filter.render()
    
    #Prepare data
    extractor = QdrantExtractorWithPayloadFilter(
        qdrant_url="http://localhost:6333",
        collection_name="newspaper_summary",
        payload_filter={
            "publish_date": {
                "gte": start_date.isoformat(),
                "lte": end_date.isoformat(),
            },
        },
    )

    news = extractor.extract()
    
    # Filter by news_type
    stock_mention = news["stocks_mention"].to_list()
    with col_right:
        input_news_type_filter = MultiSelectDropdownFilter(
            filter_name="Công ty liên quan",
            options=stock_mention,
            default=stock_mention
        )
        stock_mention = input_news_type_filter.render()

    extractor = QdrantExtractorWithPayloadFilter(
        qdrant_url="http://localhost:6333",
        collection_name="newspaper_summary",
        payload_filter={
            "publish_date": {
                "gte": start_date.isoformat(),
                "lte": end_date.isoformat(),
            },
            "stocks_mention": ["msr", "acb"],
        },
    )
    news = extractor.extract()

    # st.write(news_type)

    st.title("Tin tức thị trường")
    st.write(f"Xem tin tức thị trường đáng chú ý ngày: {start_date} đến {end_date}")

    news = news.to_dicts()
    for conv in news:
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
                st.caption(f":green[Chứng khoán liên quan: {', '.join(stocks_mention)}]")
            if fund_name:
                st.caption(f":green[Quỹ liên quan: {', '.join(fund_name)}]")

            if circular_and_policy:
                st.caption(f":red[Thông tư và chính sách liên quan: {', '.join(circular_and_policy)}]")
            if legal_documents_and_regulations:
                st.caption(f":red[Văn bản pháp luật liên quan: {', '.join(legal_documents_and_regulations)}]")  


    # st.dataframe(news)

if __name__ == "__main__":
    market_news()