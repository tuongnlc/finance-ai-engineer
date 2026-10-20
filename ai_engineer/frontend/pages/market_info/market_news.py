# from polars import date
import streamlit as st
from datetime import date


from ai_engineer.frontend.components.filter.date_filter import DateFilter


def market_news():
    # Date filter
    _, col_right = st.columns([2, 1])
    min_date = date.today()
    max_date = date.today()
    with col_right:
        input_date_filter = DateFilter(
            min_date=min_date, max_date=max_date
        )
        start_date, end_date = input_date_filter.render()

    st.title("Tin tức thị trường")
    st.write(f"Xem tin tức thị trường đáng chú ý ngày: {start_date} đến {end_date}")


if __name__ == "__main__":
    market_news()