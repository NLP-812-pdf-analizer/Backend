from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel

app = FastAPI()

@app.get("/api/health")
def health() -> str:
    return "ok"