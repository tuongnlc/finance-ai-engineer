import streamlit as st

from ai_engineer.frontend.components.markdown.markdown import MarkDown

def cash_flow():
    title = MarkDown(
        font_size="30px",    
        text="PHÂN TÍCH DÒNG TIỀN"
    ).render()

if __name__ == "__main__":
    cash_flow()
