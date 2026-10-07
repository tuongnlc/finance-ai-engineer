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

        st.metric(label=self.label, value=f"{self.prefix}{display_value}{self.suffix}")
