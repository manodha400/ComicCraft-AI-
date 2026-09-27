from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import router

app = FastAPI(title="ComicCraft - AI Comic Storyteller", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}
