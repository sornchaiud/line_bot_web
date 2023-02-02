import os

if os.getenv('API_ENV') != 'production':
    from dotenv import load_dotenv
    load_dotenv()

import uvicorn

from fastapi import FastAPI, Request

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from firebase_admin import db

from routers import database, webhooks

templates = Jinja2Templates(directory="_templates")

app = FastAPI()
app.include_router(database.router)
app.include_router(webhooks.router)

app.mount("/static", StaticFiles(directory="_statics"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    default_app = database.default_app
    users = db.reference("/users").get()
    messages = db.reference("/users/Ud1500fd6dceff152f5e6d90080de2720/messages").get()

    return templates.TemplateResponse("index.html", {
        "request": request, 
        "users": users,
        "messages": messages
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)