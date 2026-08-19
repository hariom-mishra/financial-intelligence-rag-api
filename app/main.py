from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from api.router import api_router
from core.exceptions import RAGException
from core.db import db_engine, Base
from contextlib import asynccontextmanager
import logging

# Ensure all models are imported so Base.metadata can discover them
import schema.users
import schema.user_links

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RAGApp")

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run database initialization at startup
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified/created successfully.")
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)

@app.exception_handler(RAGException)
async def rag_exception_handler(request: Request, exc: RAGException):
    logger.error(f"RAG Application Error on {request.url.path}: {exc.message} ({exc.__class__.__name__})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_type": exc.__class__.__name__
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled Internal Server Error on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected server error occurred. Please check the logs.",
            "error_type": "InternalServerError"
        }
    )

@app.get("/")
def test_connection():
    return {"message" : "Connected to financial intelligence successfully"}