import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", reload=True)
