from fastapi import FastAPI, Response, status, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import os
import tempfile
import shutil

from model.ner_inf import api_extract_graphs_from_pdf

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
    # Путь к папке с моделью, а не к конкретному файлу
    model_path = "../model"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        shutil.copyfileobj(pdfFile.file, temp_file)
        temp_file_path = temp_file.name

        try:
            # Запускаем блокирующую функцию в отдельном потоке, чтобы не блокировать event loop
            functional_graph, hierarchical_graph = await run_in_threadpool(
                api_extract_graphs_from_pdf, temp_file_path, model_path
            )
        except Exception as e:
            logger.error(f"Ошибка при обработке PDF: {e}")
            raise HTTPException(status_code=500, detail="Error processing pdf file") from e
        finally:
            os.remove(temp_file_path)

    return {
        "functional": functional_graph,
        "hierarchical": hierarchical_graph
    }


app.mount("/", StaticFiles(directory="view", html=True),name="view")