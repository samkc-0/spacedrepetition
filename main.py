from functools import lru_cache
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import dotenv_values
from fastapi import Depends, FastAPI
from routers.dashboard import dashboard_router
from routers.api import api_router
from config import Settings

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Change to match your frontend
    allow_credentials=True,  # Allow cookies
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


app.include_router(api_router)
app.include_router(dashboard_router)


@lru_cache
def get_settings():
    return Settings()


@app.get("/info")
async def info(settings: Settings = Depends(get_settings)):
    return {
        "app_name": settings.app_name,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
