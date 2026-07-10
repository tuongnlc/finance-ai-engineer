from ai_engineer.applications.chatbot.frontend.services.conversation_api import ConversationApi
from ai_engineer.applications.chatbot.frontend.services.message_api import MessageApi
from ai_engineer.applications.chatbot.frontend.services.llm_caller_api import ChatWithLLMApi
import uuid

import gradio as gr

conversation_api = ConversationApi()  # create conversation api to communicate with back-end service
message_api = MessageApi()
chat_with_llm_api = ChatWithLLMApi()

async def send_message(text, history, session=None):
    """
        Handle user sending message action
    """

    if session is None:
        session = {
            "user_id": None,
            "space_id": None,
            "conversation_id": None,
            "message_history": [],
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

            message_url="",
            status="PENDING",
        )
    except Exception as exc:
        assistant_content = f"Backend error: {type(exc).__name__}: {exc}"

    #query all messages in conversation
    messages = await message_api.get_messages_by_conversation_id(
        conversation_id=conversation_id,
    )
    message_history = [message["content"] for message in messages]

    llm_response = await chat_with_llm_api.chat_with_llm(
        id=uuid.uuid4(),
        user_question=cleaned,
        question_context="user historical chat: " + ", ".join(
            message_history 
        ),
    )
    assistant_content = llm_response["response"]

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
