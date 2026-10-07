import polars as pl
import streamlit as st


class TableChart:
    def __init__(self, title: str = ""):
        self.title = title

    def render(self, data: pl.DataFrame):
        if self.title:
            st.subheader(self.title)
        st.dataframe(data, use_container_width=True)