from dotenv import load_dotenv
from services.llm_generator import generate_response
from fastapi import FastAPI
from api.router import api_router

load_dotenv()

app = FastAPI()

app.include_router(api_router)

@app.get("/")
def test_connection():
    return {"message" : "Connected to financial intelligence successfully"}