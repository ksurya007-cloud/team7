from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from modules.ai_service import AIService

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = FastAPI(title="EduGenie", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
ai = AIService()


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)


class QARequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=10000)


class LearnRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=5000)
    level: str = Field(default="Beginner", max_length=50)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="index.html"
)

@app.get("/health")
async def health():
    return {"status": "ok", "ai_configured": ai.configured, "model": ai.model_name}


@app.post("/qa")
async def qa(payload: QARequest):
    return {"result": await ai.qa(payload.question)}


@app.post("/explain")
async def explain(payload: TextRequest):
    return {"result": await ai.explain(payload.text)}


@app.post("/quiz")
async def quiz(payload: TextRequest):
    return {"result": await ai.quiz(payload.text)}


@app.post("/summarize")
async def summarize(payload: TextRequest):
    return {"result": await ai.summarize(payload.text)}


@app.post("/learn/recommendations")
async def recommendations(payload: LearnRequest):
    return {"result": await ai.learning_path(payload.topic, payload.level)}
