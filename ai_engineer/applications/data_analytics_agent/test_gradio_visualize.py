import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import gradio as gr
import json
import polars as pl
import matplotlib

from ai_engineer.applications.data_analytics_agent.application.draw_chart import draw_pie_chart
from ai_engineer.applications.data_analytics_agent.application.processing_data import load_and_prepare_data
matplotlib.use("Agg")
import matplotlib.pyplot as plt

url = "/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/data_analytics_agent/resources/vnm/bcdkt.json"

bctc_url = "/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/data_analytics_agent/resources/vnm/bcdkt.json"
columns = ["ngay", "tai_san_ngan_han", "tai_san_dai_han"]

df_ts = load_and_prepare_data(bctc_url, columns)

fig_ts, text = draw_pie_chart(
    df=df_ts,
    date_column="ngay",
    pie_chart_elements={
        "tai_san_ngan_han": "Tài sản ngắn hạn",
        "tai_san_dai_han": "Tài sản dài hạn",
    },
    pie_chart_title="Cơ cấu tài sản ngày",
    set_legend=True,
)

#pie chart for tsnh 
columns_tsnh = [
    "ngay", 
    "tien_va_cac_khoan_tuong_duong_tien", 
    "tai_san_dai_han",
    "cac_khoan_dau_tu_tai_chinh_ngan_han",
    "cac_khoan_phai_thu_ngan_han",
    "hang_ton_kho",
    "tai_san_sinh_hoc_ngan_han",
    "tai_san_ngan_han_khac"
]

df_tsnh = load_and_prepare_data(bctc_url, columns_tsnh)
fig_tsnh, text = draw_pie_chart(
    df=df_tsnh,
    date_column="ngay",
    pie_chart_elements={
        "tien_va_cac_khoan_tuong_duong_tien": "Tiền và các khoản tương đương tiền", 
        "cac_khoan_dau_tu_tai_chinh_ngan_han": "Các khoản đầu từ tài chính ngắn hạn",
        "cac_khoan_phai_thu_ngan_han": "Các khoản phải thu ngắn hạn",
        "hang_ton_kho": "Hàng tồn kho",
        "tai_san_sinh_hoc_ngan_han": "Tài sản sinh học ngắn hạn",
        "tai_san_ngan_han_khac": "Tài sản ngắn hạn khác"
    },
    pie_chart_title="Cơ cấu tài sản ngày",
    set_legend=True,
)

#pie chart for tsdh
columns_tsdh = [
    "ngay", 
    "cac_khoan_phai_thu_dai_han", 
    "tai_san_co_dinh",
    "tai_san_sinh_hoc_dai_han",
    "bat_dong_san_dau_tu",
    "tai_san_do_dang_dai_han",
    "cac_khoan_dau_tu_tai_chinh_dai_han",
    "tai_san_dai_han_khac"
]

with gr.Blocks(title="Biểu đồ Cơ cấu Tài sản") as demo:
    gr.Markdown("### Đây là một dòng tiêu đề hoặc text hướng dẫn")
    with gr.Row():
        with gr.Column(scale=3):
            chart_out = gr.Plot(value=fig_ts, label="Biểu đồ cơ cấu tài sản")
        with gr.Column(scale=1):
            gr.Markdown("""
            ### 
            # Đây là một dòng tiêu đề hoặc text hướng dẫn
            # Dòng này là một dòng tiêu đề hoặc text hướng dẫn
            # Dòng này là một dòng tiêu đề hoặc text hướng dẫn
            # 
        """)
    gr.Markdown("### Đây là một dòng tiêu đề hoặc text hướng dẫn")
    with gr.Row():
        with gr.Column(scale=10):
            chart_out = gr.Plot(value=fig_tsnh, label="Biểu đồ cơ cấu tài sản")


if __name__ == "__main__":
    demo.launch()
