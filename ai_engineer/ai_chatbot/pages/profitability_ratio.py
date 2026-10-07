import streamlit as st


def profitability_ratio():
    st.set_page_config(
        page_title="Profitability Ratio",
        layout="wide"  
    )

    st.markdown(
        """
        <p style='font-size: 30px; font-weight: bold;color: #1583b4;'>PHÂN TÍCH KHẢ NĂNG SINH LỢI</p>
        """,
        unsafe_allow_html=True,
    )

    st.write(
        """
            Trong báo cáo này, chúng ta sẽ phân tích cách công ty sử dụng vốn và nợ 
            như thế nào để tạo ra doanh thu và lợi nhuận. 

            Tập trung vào hoạt động kinh doanh cốt lõi của công ty            
            - 1: Doanh thu
            - 2: Lợi nhuận
        """
    )


if __name__ in {"__main__", "__page__"}:
    profitability_ratio()
