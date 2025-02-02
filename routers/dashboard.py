from fastapi.responses import HTMLResponse, RedirectResponse
from dotenv import dotenv_values
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from models import User
from routers.api import login_for_access_token


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
) -> HTMLResponse:
    token = await login_for_access_token(form_data)
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
