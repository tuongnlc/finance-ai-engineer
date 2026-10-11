import streamlit as st


class KpiCardChart:
    """
        Single KPI card component. Renders exactly one metric card per instance.

        Args:
            label (str): KPI label shown above the value.
            prefix (str, optional): Prepended to the formatted value.
            suffix (str, optional): Appended to the formatted value.
            format (str, optional): Python format string e.g. "{:,.0f}" or "{:.2%}".
        Returns:
            None
    """
    def __init__(
        self,
        label: str = "",
        prefix: str = "",
        suffix: str = "",
        format: str = "{:,.0f}",
    ):
        self.label = label
        self.prefix = prefix
        self.suffix = suffix
        self.format = format

    def render(self, value: int | float | None):
        if value is None:
            display_value = "—"
        else:
            try:
                native = float(value)
                display_value = self.format.format(native)
            except (ValueError, TypeError):
                try:
                    native = int(float(value))
                    display_value = self.format.format(native)
                except (ValueError, TypeError):
                    display_value = str(value)

        st.markdown(
            f"""
            <div style="
                border: none;
                border-radius: none;
                padding: 16px 20px;
                background-color: transparent;
                height: 100%;
            ">
                <div style="
                    font-size: 14px;
                    color: #31333F;
                    font-weight: 600;
                    line-height: 1.4;
                    margin-bottom: 8px;
                    white-space: pre-wrap;
                    word-break: break-word;
                ">{self.label}</div>
                <div style="
                    font-size: 28px;
                    font-weight: 700;
                    color: #262730;
                    line-height: 1.2;
                ">{self.prefix}{display_value}{self.suffix}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
