from fastapi import FastAPI, Response, status, HTTPException, UploadFile, File
from pydantic import BaseModel
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="pdf loader", root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health() -> bool:
    return True

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # Здесь ваша ML-логика: обработка contents в пайплайне
    # запускаем функцию-затычку, которая 
    # загружаем класс-сервис и передает туда пдф, получая жсон
    # для начала просто извлекаем текст
    # затем создадим связь с другим микросервисом, куда перенесем этот класс
    return {"message": f"Файл {file.filename} получен и обработан"}