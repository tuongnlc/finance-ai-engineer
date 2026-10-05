import polars as pl
import streamlit as st
import altair as alt


class LineChartComponent:
    """
        Line chart component. Using to render line chart or multiple line chart.

        Args:
            title (str, optional): Title of the chart. Defaults to "".
            x_col (str, optional): Column name of the x-axis. Defaults to "".
            y_cols (list[str], optional): Column names of the y-axis. Defaults to None.
            y_min (float, optional): Minimum value of the y-axis. Defaults to None.
            y_max (float, optional): Maximum value of the y-axis. Defaults to None.
        Returns:
            None
    """
    def __init__(
        self,
        title: str = "",
        x_col: str = "",
        y_cols: list[str] | None = None,
        y_min: float | None = None,
        y_max: float | None = None,
    ):
        self.title = title
        self.x_col = x_col
        self.y_cols = y_cols or []
        self.y_min = y_min
        self.y_max = y_max

    def render(self, data: pl.DataFrame):
        if self.title:
            st.markdown(
                f'<p style="font-size: 1rem; font-weight: 600; margin: 0.2rem 0 0.5rem 0;">{self.title}</p>',
                unsafe_allow_html=True,
            )
        if not self.x_col or not self.y_cols:
            st.line_chart(data, use_container_width=True)
            return

        chart_df = (
            data.select([self.x_col, *self.y_cols])
            .unpivot(index=self.x_col, on=self.y_cols, variable_name="series", value_name="value")
        )

        y_domain = [self.y_min, self.y_max] if self.y_min is not None or self.y_max is not None else alt.Undefined

        base = alt.Chart(chart_df).encode(
            x=alt.X(f"{self.x_col}:N", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("value:Q", scale=alt.Scale(domain=y_domain)),
            color=alt.Color("series:N", legend=alt.Legend(orient="bottom", titleOrient="left")),
        )

        line = base.mark_line(point=True)
        text = base.mark_text(
            align="center",
            baseline="bottom",
            dy=-5,
            fontSize=9,
        ).encode(
            text=alt.Text("value:Q", format=",.2f")
        )

        chart = (
            alt.layer(line, text)
            .properties(
                width="container",
                height=200,
            )
            .configure_legend(
                orient="bottom",
                title=None,
            )
        )
        st.altair_chart(chart, use_container_width=True)