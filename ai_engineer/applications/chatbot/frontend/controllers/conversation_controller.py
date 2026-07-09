# from ai_engineer.applications.chatbot.frontend.services.conversation_api import ConversationApi
# import gradio as gr

# api = ConversationApi() # create conversation api to communicate with back-end service


# async def send_message(text, history, model, session=None):
#     """
#         Handle user sending message action
#     """
#     if session is None:
#         session = {
#             "user_id": None,
#             "space_id": None,
#             "conversation_id": None,
#         }

#     cleaned = (text or "").strip()
#     if not cleaned:
#         current_history = history or []
#         return (
#             gr.update(value=current_history, visible=bool(current_history)),
#             "",
#             gr.update(interactive=False, visible=False),
#             session,
#         )

#     try:
#         response = await api.create_conversation(
#             content=cleaned,
#             user_id=(session or {}).get("user_id"),
#             space_id=(session or {}).get("space_id"),
#         )
#         # assistant_content = f"created: {response['id']}"
#         assistant_content = f"{text}"
#         session["conversation_id"] = response["id"]
#     except Exception as e:
#         assistant_content = f"Backend error: {type(e).__name__}: {e}"

#     next_history = (history or []) + [
#         {"role": "user", "content": cleaned},
#         {"role": "assistant", "content": assistant_content},
#     ]

#     return (
#         gr.update(value=next_history, visible=True),
#         "",
#         gr.update(interactive=False, visible=False),
#         session,
#     )
