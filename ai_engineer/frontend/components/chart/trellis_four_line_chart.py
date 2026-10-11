# ai_engineer/frontend/components/chart/chart_grid.py
import polars as pl
import streamlit as st
from ai_engineer.frontend.components.chart.line_chart import LineChartComponent

class TrellisFourLineChartComponent:
    """Render một grid các LineChartComponent trong container có border.

    Args:
        chart_configs: list các dict chứa tham số của LineChartComponent
                       (title, x_col, y_cols, y_min, y_max)
        cols_per_row: số cột mỗi hàng (mặc định 2)
    """
    def __init__(self, chart_configs: list[dict], cols_per_row: int = 2):
        self.chart_configs = chart_configs
        self.cols_per_row = cols_per_row

    def render(self, data: pl.DataFrame):
        with st.container(border=True):
            for i in range(0, len(self.chart_configs), self.cols_per_row):
                row = self.chart_configs[i:i + self.cols_per_row]
                cols = st.columns(self.cols_per_row)
                for col, cfg in zip(cols, row):
                    with col:
                        LineChartComponent(**cfg).render(data)