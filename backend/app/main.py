from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import chat, analytics, feedback
from .database import Base, engine


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="Intelligent Customer Support Chatbot API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat.router, prefix="/api")
    app.include_router(analytics.router, prefix="/api")
    app.include_router(feedback.router, prefix="/api")

    return app


app = create_app()

