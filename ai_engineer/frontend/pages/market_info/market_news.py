# from polars import date
import streamlit as st
from datetime import date, timedelta


from ai_engineer.frontend.components.filter.date_filter import DateFilter
from ai_engineer.shared.data_pipeline.extract.qdrant_extractor import QdrantExtractorWithPayloadFilter




def market_news():
    

    # Date filter
    _, col_right = st.columns([2, 1])
    max_date = date.today()
    min_date = max_date - timedelta(days=90)
    with col_right:
        input_date_filter = DateFilter(
            min_date=min_date, max_date=max_date
        )
        start_date, end_date = input_date_filter.render()

    st.title("Tin tức thị trường")
    st.write(f"Xem tin tức thị trường đáng chú ý ngày: {start_date} đến {end_date}")

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
    news = news.to_dicts()
    # news = news.select(["newspaper_summary"])

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