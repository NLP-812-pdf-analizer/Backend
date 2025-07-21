from fastapi import FastAPI, Response, status, HTTPException, UploadFile, File
from pydantic import BaseModel
import requests
from fastapi.middleware.cors import CORSMiddleware
from typing import List


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health() -> str:
    return "ok"

@app.post("/api/graph")
def get_graph(pdfFile: UploadFile = File(...)):
    # Здесь ваша ML-логика: обработка contents в пайплайне
    # запускаем функцию-затычку, которая 
    # загружаем класс-сервис и передает туда пдф, получая жсон
    # для начала просто извлекаем текст
    # затем создадим связь с другим микросервисом, куда перенесем этот класс
    return {"received_file": pdfFile.filename}