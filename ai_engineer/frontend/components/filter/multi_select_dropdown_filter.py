import streamlit as st


class MultiSelectDropdownFilter:
    def __init__(self, filter_name: str, options: list[dict], default: list[dict] = None):
        self.filter_name = filter_name
        self.options = options
        self.default = default

    def render(self):
        return st.multiselect(
            self.filter_name,
            options=self.options,
            default=self.default if self.default is not None else self.options,
        )