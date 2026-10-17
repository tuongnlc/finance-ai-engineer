import streamlit as st

from ai_engineer.frontend.components.markdown.markdown import MarkDown


def debt_management_ratio():
    st.set_page_config(
        page_title="Debt Management Ratio",
        layout="wide"  
    )

    title = MarkDown(
        font_size="30px",    
        text="PHÂN TÍCH KHẢ NĂNG QUẢN TRỊ NỢ"
    ).render()

    st.write(
        """
            Trong báo cáo này, chúng ta sẽ phân tích khả năng quản trị nợ của công ty.
            + Tỉ lệ giữa nợ và tổng tài sản và nợ trên vốn
            + Khả năng chi trả lãi vay của doanh nghiệp
            + Khả năng thanh toán nợ của doanh nghiệp
        """
    )

if __name__ == "__main__":
    debt_management_ratio()