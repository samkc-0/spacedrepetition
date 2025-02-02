import random
from fastapi.responses import HTMLResponse, RedirectResponse
from dotenv import dotenv_values
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from auth import get_current_user_cookie
from db import get_session
from models import Memory, Question, Sentence, User, Word
from routers.api import get_next_memory, login_for_access_token


config = dotenv_values(".env")

templates = Jinja2Templates(directory="templates")
dashboard_router = APIRouter(tags=["DASHBOARD"])


@dashboard_router.get("/", response_class=RedirectResponse)
async def home(request: Request):
    return RedirectResponse(url="/login")


@dashboard_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        name="/dashboard.html", context={"request": request}
    )


@dashboard_router.get("/login", response_class=HTMLResponse)
async def get_login_form(request: Request):
    return templates.TemplateResponse(name="/login.html", context={"request": request})


@dashboard_router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> HTMLResponse:
    token = await login_for_access_token(form_data, session)
    response = templates.TemplateResponse(
        name="/dashboard.html", context={"request": request}
    )
    # response.delete_cookie("Authorization")
    response.set_cookie(
        "Authorization",
        value=f"Bearer {token.access_token}",
        httponly=True,
        max_age=1800,
        expires=1800,
        samesite="Lax",
        secure=False,
    )
    # response.headers["HX-LOCATION"] = "/dashboard"
    return response


@dashboard_router.get("/register", response_class=HTMLResponse)
async def get_login_form(request: Request):
    return templates.TemplateResponse(
        name="/register.html", context={"request": request}
    )


@dashboard_router.get("/review")
async def get_login_form(
    request: Request,
    user: User = Depends(get_current_user_cookie),
    session: Session = Depends(get_session),
):
    memories = session.exec(select(Memory).order_by(Memory.due_date).limit(1))
    memory = memories.first()
    word = session.get(Word, memory.word_id)
    sentence = random.choice(
        session.exec(select(Sentence).where(Sentence.word_id == word.id)).all()
    )
    question = Question(memory=memory, word=word, sentence=sentence)
    text = question.sentence.text
    return templates.TemplateResponse(
        name="/dashboard.html",
        context={"request": request, "question": text},
    )
