import gradio as gr

from ai_engineer.applications.chatbot.frontend.controllers.conversation_controller import send_message


def build_demo() -> gr.Blocks:
    css = """
      body, .gradio-container {
        min-height: 100vh;
        background: radial-gradient(1200px 600px at 50% 20%, #111b3a 0%, #070a14 55%, #05060b 100%);
      }
      #hero {
        max-width: 980px;
        margin: 0 auto;
        padding: 140px 16px 22px 16px;
        text-align: center;
      }
      #hero h1 {
        font-size: 52px;
        font-weight: 650;
        margin: 0;
        line-height: 1.15;
        color: rgba(255, 255, 255, 0.92);
        letter-spacing: -0.02em;
      }
      #composer {
        max-width: 980px;
        margin: 0 auto;
        padding: 12px 16px;
        background: rgba(25, 28, 36, 0.60);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 999px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        align-items: center;
        gap: 10px;
      }
      #composer button { 
        height: 44px;
        min-width: 44px;
        padding: 0 10px !important;
        border-radius: 999px !important;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        color: rgba(255, 255, 255, 0.88) !important;
        font-weight: 600;
      }
      #composer button:hover {
        background: rgba(255, 255, 255, 0.06) !important;
      }
      #composer button:disabled {
        opacity: 0.45;
      }
      #composer > .wrap {
        gap: 10px;
      }
      #composer .block, #composer .wrap, #composer .wrap * {
        border-color: rgba(255, 255, 255, 0.0) !important;
      }
      #composer .block, #composer .wrap {
        background: transparent !important;
        box-shadow: none !important;
      }
      #message-wrap {
        flex: 1;
        min-width: 260px;
      }
      #message-wrap .wrap, #message-wrap .wrap * {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
      }
      #message-wrap textarea, #message-wrap input {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: rgba(255, 255, 255, 0.92) !important;
        font-size: 16px;
        padding: 10px 6px !important;
      }
      #message-wrap textarea::placeholder, #message-wrap input::placeholder {
        color: rgba(255, 255, 255, 0.55) !important;
      }
      #model-wrap {
        width: 120px;
      }
      #model-wrap .wrap, #model-wrap .wrap * {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: rgba(255, 255, 255, 0.90) !important;
      }
      #model-wrap .wrap {
        padding: 0 !important;
      }
      #send-btn button {
        background: rgba(255, 255, 255, 0.10) !important;
      }
      #send-btn button:hover {
        background: rgba(255, 255, 255, 0.14) !important;
      }
      #chat-wrap {
        max-width: 980px;
        margin: 0 auto;
        padding: 8px 16px 40px 16px;
      }
      #chat-wrap .bubble-wrap {
        background: rgba(0, 0, 0, 0.0);
      }
      footer { display: none !important; }
    """

    with gr.Blocks(css=css, theme=gr.themes.Soft()) as demo:
        gr.HTML("<div id='hero'><h1>Bạn cứ hỏi đi, cat tuong!</h1></div>")

        chat = gr.Chatbot(label=None, visible=False, elem_id="chat-wrap")
        session = gr.State(
            {
                "user_id": None,
                "space_id": None,
                "conversation_id": None,
            }
        )

        with gr.Row(elem_id="composer", equal_height=True):
            attach_btn = gr.Button("＋", elem_id="attach-btn", scale=0, min_width=44)
            message = gr.Textbox(
                placeholder="Hỏi Gemini",
                label=None,
                show_label=False,
                container=False,
                elem_id="message-wrap",
                scale=8,
                min_width=320,
            )
            model = gr.Dropdown(
                choices=["Flash", "Pro"],
                value="Flash",
                label=None,
                show_label=False,
                container=False,
                elem_id="model-wrap",
                scale=0,
                min_width=110,
            )
            mic_btn = gr.Button("🎙", elem_id="mic-btn", scale=0, min_width=44)
            send_btn = gr.Button("➤", elem_id="send-btn", interactive=False, visible=False, scale=0, min_width=44)

        def _toggle_send_btn(text: str):
            has_text = bool((text or "").strip())
            return gr.update(interactive=has_text, visible=has_text)

        message.input(fn=_toggle_send_btn, inputs=message, outputs=send_btn)
        message.change(fn=_toggle_send_btn, inputs=message, outputs=send_btn)

        send_btn.click(
            fn=send_message,
            inputs=[message, chat, model, session],
            outputs=[chat, message, send_btn, session],
            queue=False,
        )
        message.submit(
            fn=send_message,
            inputs=[message, chat, model, session],
            outputs=[chat, message, send_btn, session],
            queue=False,
        )

        attach_btn.click(fn=lambda: None, inputs=None, outputs=None, queue=False)
        mic_btn.click(fn=lambda: None, inputs=None, outputs=None, queue=False)

    return demo
