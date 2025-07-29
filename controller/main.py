from fastapi import FastAPI, Response, status, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
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
        shutil.copyfileobj(pdfFile.file, temp_file)
        temp_file_path = temp_file.name

        try:
            # вызов функции АПИ модели
            functional_graph, hierarchical_graph = 100,200 #await model(temp_file_path)  # Assuming model is an async function
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error processing pdf file") from e
        finally:
            os.remove(temp_file_path)

    return {
        "functional": functional_graph,
        "hierarchical": hierarchical_graph
    }


app.mount("/", StaticFiles(directory="view", html=True),name="view")