import polars as pl
import streamlit as st


@st.cache_data(ttl=600)  # Cache dữ liệu trong 10 phút
def load_data_from_postgres_polars(query: str):
  """Hàm kết nối PostgreSQL và trả về Polars DataFrame"""
  try:
    # Lấy thông tin cấu hình từ file secrets.toml
    db_config = st.secrets["postgres"]

    # Tạo connection string (URI) cho PostgreSQL
    # Định dạng: postgresql://user:password@host:port/database
    uri = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

    df = pl.read_database_uri(query=query, uri=uri, engine="adbc")

    return df

  except Exception as e:
    st.error(f"Lỗi kết nối CSDL: {e}")
    return pl.DataFrame()  # Trả về Polars DataFrame rỗng nếu lỗi