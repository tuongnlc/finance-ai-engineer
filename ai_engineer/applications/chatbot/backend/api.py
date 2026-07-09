from fastapi import FastAPI
from .routes import health, conversation, message



def create_chatbot_api():
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
    return app


app = create_chatbot_api()
