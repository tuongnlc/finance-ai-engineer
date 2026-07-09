from ai_engineer.applications.chatbot.frontend.services.conversation_api import ConversationApi
from ai_engineer.applications.chatbot.frontend.services.message_api import MessageApi

import gradio as gr

conversation_api = ConversationApi()  # create conversation api to communicate with back-end service
message_api = MessageApi()

async def send_message(text, history, session=None):
    """
        Handle user sending message action
    """

    if session is None:
        session = {
            "user_id": None,
            "space_id": None,
            "conversation_id": None,
        }

    cleaned = (text or "").strip()
    if not cleaned:
        current_history = history or []
        return (
            gr.update(value=current_history, visible=bool(current_history)),
            "",
            gr.update(interactive=False, visible=False),
            session,
        )

    conversation_id = session.get("conversation_id")
    assistant_content = cleaned

    #create conversation if not exist
    try:
        if not conversation_id:
            conversation = await conversation_api.create_conversation(
                content=cleaned,
                user_id="tuongnlc",
                space_id=session.get("space_id"),
            )
            session["conversation_id"] = conversation["id"]
            conversation_id = session["conversation_id"]
    except Exception as exc:
        assistant_content = f"Backend error: {type(exc).__name__}: {exc}"

    #create message 
    try:
        await message_api.create_message(
            content=cleaned,
            conversation_id=conversation_id,
            user_id="tuongnlc",
            space_id=session.get("space_id"),
            content_type="text",
            message_url="",
            status="PENDING",
            attachments=""
        )
    except Exception as exc:
        assistant_content = f"Backend error: {type(exc).__name__}: {exc}"

    next_history = (history or []) + [
        {"role": "user", "content": cleaned},
        {"role": "assistant", "content": assistant_content},
    ]

    return (
        gr.update(value=next_history, visible=True),
        "",
        gr.update(interactive=False, visible=False),
        session,
    )
