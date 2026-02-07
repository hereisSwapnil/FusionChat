from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import init_db
from app.api.endpoints.chats import router as chat_router
from app.api.endpoints.ingestion import router as ingestion_router

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://frontend:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(ingestion_router)


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}
