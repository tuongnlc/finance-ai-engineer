from fastapi import FastAPI

from ai_engineer.shared.observability.mlflow_config import setup_mlflow

from .routes import conversation, health, llm_response, message, rag, ai_chat



def create_chatbot_api():
    setup_mlflow()
    app = FastAPI(
        title="Chatbot API",
        version="1.0",
        description="API for chatbot",
        contact={"name": "Tuong Nguyen"},
        license={"name": "MIT License"},
    )
    app.include_router(health.router)
    app.include_router(conversation.router)
    app.include_router(message.router)
    app.include_router(llm_response.router)
    app.include_router(rag.router)
    app.include_router(ai_chat.router)
    return app


app = create_chatbot_api()
