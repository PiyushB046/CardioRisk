import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import select, text

from src.heart.config import METRICS_PATH
from src.heart.db import Prediction, SessionLocal, engine, init_db
from src.heart.predict import predict

WEB = Path(__file__).resolve().parents[1] / "web"


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Heart Disease Prediction API", version="1.0", lifespan=lifespan)


class Patient(BaseModel):
    age: int = Field(ge=1, le=120)
    sex: Literal[0, 1]
    cp: Literal[1, 2, 3, 4]
    trestbps: Optional[float] = Field(None, ge=50, le=250)
    chol: Optional[float] = Field(None, ge=80, le=700)
    fbs: Optional[Literal[0, 1]] = None
    restecg: Optional[Literal[0, 1, 2]] = None
    thalach: Optional[float] = Field(None, ge=50, le=230)
    exang: Optional[Literal[0, 1]] = None
    oldpeak: Optional[float] = Field(None, ge=-3, le=7)
    slope: Optional[Literal[1, 2, 3]] = None
    ca: Optional[Literal[0, 1, 2, 3]] = None
    thal: Optional[Literal[3, 6, 7]] = None


@app.get("/api/health")
def health():
    with engine.connect() as c:
        c.execute(text("select 1"))
    return {"status": "ok"}


@app.post("/api/predict")
def do_predict(p: Patient):
    rec = p.model_dump()
    out = predict(rec)
    with SessionLocal() as s:
        s.add(Prediction(inputs=rec, probability=out["probability"], label=out["label"], model_name=out["model"]))
        s.commit()
    return out


@app.get("/api/metrics")
def metrics():
    if not METRICS_PATH.exists():
        raise HTTPException(404, "Model not trained yet: run python -m src.heart.train")
    return json.loads(METRICS_PATH.read_text())


@app.get("/api/history")
def history(limit: int = 25):
    with SessionLocal() as s:
        rows = s.scalars(select(Prediction).order_by(Prediction.id.desc()).limit(min(limit, 200))).all()
    return [{"id": r.id, "created_at": r.created_at.isoformat(), "inputs": r.inputs,
             "probability": r.probability, "label": r.label, "model": r.model_name} for r in rows]


app.mount("/static", StaticFiles(directory=WEB), name="static")


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")
