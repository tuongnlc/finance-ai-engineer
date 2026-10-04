import streamlit as st
import pandas as pd
import psycopg2

# Sử dụng @st.cache_data để Streamlit không phải query lại CSDL mỗi khi người dùng bấm nút (tăng tốc độ)
@st.cache_data(ttl=600) # Dữ liệu sẽ được cache trong 10 phút
def load_data_from_postgres():
    """Hàm kết nối PostgreSQL và trả về DataFrame"""
    try:
        # Lấy thông tin cấu hình từ file secrets.toml
        db_config = st.secrets["postgres"]
        
        # Tạo kết nối đến PostgreSQL
        connection = psycopg2.connect(
            host=db_config["host"],
            port=db_config["port"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"]
        )
        
        # Truy vấn dữ liệu (Thay 'your_table_name' bằng tên bảng thực tế của bạn)
        query = "SELECT * FROM your_table_name;"
        df = pd.read_sql(query, connection)
        
        return df
        
    except Exception as e:
        st.error(f"Lỗi kết nối CSDL: {e}")
        return pd.DataFrame() # Trả về DataFrame rỗng nếu lỗi
        
    finally:
        # Đảm bảo đóng kết nối nếu đã mở thành công
        if 'connection' in locals() and connection:
            connection.close()