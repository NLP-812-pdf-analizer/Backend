from fastapi import FastAPI, Response, status, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
import requests
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import os
import tempfile
import shutil

#from model.<main>.<ml entrypoint>

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health() -> str:
    return "ok"

@app.post("/api/graph")
async def get_graph(pdfFile: UploadFile = File(...)):
    # Здесь вызов ML-логика: обработка contents в пайплайне
    # запускаем функцию-затычку, которая 
    # загружаем класс-сервис и передает туда пдф, получая жсон
    # для начала просто извлекаем текст
    # затем создадим связь с другим микросервисом, куда перенесем этот класс
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:



    try:
        file_content = await pdfFile.read()
        # передача в скрипт для извлечения

        # получаем байтовый объект со строками?

        model_url = os.getenv("MODEL_URL")
        if not model_url:
            return {"error": "MODEL_URL is not set in env"}
        
        request = {
            "text" : [] # массив строк
        }

        try:
            model_response = requests.post(model_url, json=request)
            model_response.raise_for_status()
            graph_data = model_response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error with model requst: {e}")

        return graph_data

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing pdf file") from e
    finally:
        pdfFile.file.close()

app.mount("/", StaticFiles(directory="view", html=True),name="view")