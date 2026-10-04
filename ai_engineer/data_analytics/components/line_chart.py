import pandas as pd
import streamlit as st


class LineChartComponent:
    def __init__(self, title: str = "", x_col: str = "", y_col: str = ""):
        self.title = title
        self.x_col = x_col
        self.y_col = y_col

    def render(self, data: pd.DataFrame):
        if self.title:
            st.subheader(self.title)
        if self.x_col and self.y_col:
            chart_data = data.set_index(self.x_col)[self.y_col] if isinstance(self.y_col, str) else data.set_index(self.x_col)[self.y_col]
            st.line_chart(chart_data, use_container_width=True)
        else:
            st.line_chart(data, use_container_width=True)
