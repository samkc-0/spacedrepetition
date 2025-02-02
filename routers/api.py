from datetime import timedelta
import random
from fastapi.responses import RedirectResponse
from dotenv import dotenv_values
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from auth import (
    ACCESS_TOKEN_EXPIRES_MINUTES,
    Token,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_user_cookie,
)
from db import User, get_session
from models import Answer, Memory, Question, Sentence, Word
from memory import srs_algorithm


api_router = APIRouter(prefix="/api", tags=["API"])


@api_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username of password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    access_token = create_access_token(
        {"sub": user.username}, expires_delta=expires_delta
    )
    token = Token(access_token=access_token, token_type="bearer")
    return token


@api_router.get(
    "/user/whoami",
    response_model=User,
    dependencies=[Depends(get_current_user_cookie)],
)
async def read_users_me(current_user: User = Depends(get_current_user_cookie)) -> User:
    return current_user


@api_router.get("/user/{user_id}", status_code=status.HTTP_401_UNAUTHORIZED)
async def get_user_profile(
    user_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> User:
    return session.get(User, user_id)


@api_router.post("/user/create", status_code=status.HTTP_201_CREATED)
async def create_user(user: User, session: Session = Depends(get_session)) -> User:
    session.add(user)
    session.flush()
    session.commit()
    session.refresh(user)
    return user


@api_router.post("/register", status_code=status.HTTP_201_CREATED)
async def submit_regsitration_form(
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    session.refresh(user)
    # user = await create_user(user)
    return {"message": f"Created user {user.username}"}


@api_router.get("/review", status_code=status.HTTP_200_OK)
async def get_next_memory(
    User: User = Depends(get_current_user_cookie),
    session: Session = Depends(get_session),
) -> Question:
    memory = session.exec(select(Memory).order_by(Memory.due_date).limit(1)).first()
    word = session.get(Word, memory.word_id)
    sentence = random.choice(
        session.exec(select(Sentence).where(Sentence.word_id == word.id)).all()
    )
    return Question(memory=memory, word=word, sentence=sentence)


@api_router.post("/review", status_code=status.HTTP_200_OK)
async def get_next_memory(
    answer: Answer,
    session: Session = Depends(get_session),
) -> Memory:
    memory = session.get(Memory, answer.memory_id)
    memory = srs_algorithm(memory, answer.correct)
    session.add(memory)
    session.commit()
    session.refresh(memory)
    return memory
