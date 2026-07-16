from datetime import date
from ai_engineer.applications.chatbot.frontend.services.conversation_api import ConversationApi
from ai_engineer.applications.chatbot.frontend.services.message_api import MessageApi
from ai_engineer.applications.chatbot.frontend.services.llm_caller_api import ChatWithLLMApi, VietnamTextFormatAPI
from ai_engineer.applications.chatbot.frontend.services.llm_response_api import LLMResponseApi
from ai_engineer.applications.chatbot.frontend.services.rag_servicce_api import RAGServiceApi

import uuid

import gradio as gr

conversation_api = ConversationApi()  # create conversation api to communicate with back-end service
message_api = MessageApi()
chat_with_llm_api = ChatWithLLMApi()
llm_response_api = LLMResponseApi()
rag_service_api = RAGServiceApi()
vietnam_text_format_api = VietnamTextFormatAPI()

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
        message_id = uuid.uuid4()
        await message_api.create_message(
            id=message_id,
            content=cleaned,
            conversation_id=conversation_id,
            user_id="tuongnlc",
            space_id=session.get("space_id"),
            message_url="",
            status="PENDING",
        )
    except Exception as exc:
        assistant_content = f"Backend error: {type(exc).__name__}: {exc}"

    # #query all messages in conversation
    messages = await message_api.get_messages_by_conversation_id(
        conversation_id=conversation_id,
    )
    message_history = [message["content"] for message in messages]
    user_historical_chat = "User historical chat: " + ", ".join(message_history)

    #calll back-end to format query
    formatted_query = await vietnam_text_format_api.format_text(
        id=uuid.uuid4(),
        user_question=cleaned,
        question_context="string",
    )
    formatted_query = formatted_query["response"]

    # #Add context by query vector db
    rag_response = await rag_service_api.get_documents_with_user_query(
        user_query=formatted_query,
    )
    print("rag response is")
    print(rag_response)

    if len(rag_response.get("results")) == 0:
        question_context = ""
    else:
        adding_content_from_rag = []
        for document in rag_response["results"]:
            title = document["title"]
            content = document["content"]
            adding_content_from_rag.append(f"{title}: {content}")

        # #Create question context from user historical chat and rag response
        question_context = user_historical_chat + ", Related document:" + ", ".join(adding_content_from_rag)

    # print(formatted_query)
    print(question_context)

    #Call llm with question context
    llm_response = await chat_with_llm_api.chat_with_llm(
        id=uuid.uuid4(),
        user_question=formatted_query,
        question_context=question_context,
    )
    assistant_content = llm_response["response"]

    next_history = (history or []) + [
        {"role": "user", "content": cleaned},
        {"role": "assistant", "content": assistant_content},
    ]

    # #write llm response to db
    await llm_response_api.create_llm_response(
        id=uuid.uuid4(),
        message_id=message_id,
        conversation_id=conversation_id,
        llm_response=assistant_content,
        content_type="TEXT",
        attachments=None,
        created_at=date.today(),
    )

    return (
        gr.update(value=next_history, visible=True),
        "",
        gr.update(interactive=False, visible=False),
        session,
    )