import gradio as gr
# import pandas as pd
# import numpy as np
# import random

# df = pd.DataFrame({
#     'height': np.random.randint(50, 70, 25),
#     'weight': np.random.randint(120, 320, 25),
#     'age': np.random.randint(18, 65, 25),
#     'ethnicity': [random.choice(["white", "black", "asian"]) for _ in range(25)]
# })

# with gr.Blocks() as demo:
#     gr.LinePlot(df, x="weight", y="height")

# demo.launch()

import gradio as gr

with gr.Blocks(title="Trang Chào Mừng") as demo:
    gr.Markdown("Đây là trang giao diện chào mừng cơ bản.")

    info_box = gr.Textbox(
      value="Đây là nội dung văn bản nằm trong khung cố định.",
      label="Khung thông tin",
      interactive=False,  # Giúp người dùng không chỉnh sửa được
    )

demo.launch()