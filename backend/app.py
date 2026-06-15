from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, List
import json
from pathlib import Path
import os

from backend.agente_metro import AgenteMetroSantiago

LOGS_FILE = Path("./logs/agent_logs.jsonl")

class Query(BaseModel):
    query: str

app = FastAPI(title="Agente Metro API")

@app.on_event("startup")
def startup_event():
    # Inicializa el agente una vez
    app.state.agente = AgenteMetroSantiago()
    app.state._in_memory_logs = []  # cache conveniente

def _read_logs(limit: int = 100) -> List[Any]:
    if not LOGS_FILE.exists():
        return []
    lines = []
    with open(LOGS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                lines.append(json.loads(line))
            except Exception:
                continue
    return lines[-limit:]

@app.post("/api/query")
def api_query(q: Query):
    agente: AgenteMetroSantiago = app.state.agente
    try:
        respuesta = agente.procesar_consulta(q.query)
        # actualizar cache de logs leyendo la última entrada
        recent = _read_logs(limit=10)
        app.state._in_memory_logs = recent
        return {"response": respuesta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs")
def api_logs(limit: int = 100):
    logs = _read_logs(limit=limit)
    return {"count": len(logs), "logs": logs}

@app.get("/api/metrics")
def api_metrics():
    logs = _read_logs(limit=1000)
    if not logs:
        return {"count": 0, "latency_avg": 0, "latency_max": 0, "error_rate": 0}
    count = len(logs)
    latencies = [l.get("latency_seconds", 0) for l in logs if l.get("latency_seconds") is not None]
    errors = sum(1 for l in logs if l.get("error"))
    return {
        "count": count,
        "latency_avg": sum(latencies) / len(latencies) if latencies else 0,
        "latency_max": max(latencies) if latencies else 0,
        "error_rate": errors / count if count else 0,
    }
