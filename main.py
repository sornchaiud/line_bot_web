import os

if os.getenv('API_ENV') != 'production':
    from dotenv import load_dotenv
    load_dotenv()

import uvicorn

from fastapi import FastAPI

from routers import database

app = FastAPI()
app.include_router(database.router)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)