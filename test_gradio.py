import gradio as gr
import time
from test_qdrant_semantic_search import search_semantic, scroll_database

def processing_function(user_query: str):
    output_points = search_semantic(user_query)

    titles = scroll_database(output_points)
    return titles


def analyze_sentiment(user_query: str):
    result = processing_function(user_query)
    return result


def _show_loading():
    return (
        gr.update(visible=True),
        gr.update(interactive=False),
        gr.update(interactive=False),
    )


def _hide_loading():
    return (
        gr.update(visible=False),
        gr.update(interactive=True),
        gr.update(interactive=True),
    )


with gr.Blocks() as demo:
    input_text = gr.Textbox(placeholder="Nhập câu cần phân tích...")
    run_btn = gr.Button("Phân tích")
    loading = gr.Markdown("Đang xử lý...", visible=False)
    output_text = gr.Textbox(label="Kết quả")

    (
        run_btn.click(_show_loading, inputs=None, outputs=[loading, run_btn, input_text], queue=False)
        .then(analyze_sentiment, inputs=input_text, outputs=output_text)
        .then(_hide_loading, inputs=None, outputs=[loading, run_btn, input_text], queue=False)
    )

demo.queue().launch()
