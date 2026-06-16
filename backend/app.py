from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, List
import json
from pathlib import Path
import os

from backend.agent import AgenteMetroSantiago
import asyncio
from pathlib import Path
import os
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

ALERTS_FILE = Path("./logs/agent_alerts.jsonl")

# Configurables via env
ALERT_P95_THRESHOLD = float(os.getenv("P95_THRESHOLD_S", "2.0"))
ALERT_ERROR_RATE_THRESHOLD = float(os.getenv("ERROR_RATE_THRESHOLD", "0.05"))
ALERT_CHECK_INTERVAL = int(os.getenv("ALERT_CHECK_INTERVAL_S", "60"))

LOGS_FILE = Path("./logs/agent_logs.jsonl")

class Query(BaseModel):
    query: str

app = FastAPI(title="Agente Metro API")

@app.on_event("startup")
def startup_event():
    # Inicializa el agente una vez
    app.state.agente = AgenteMetroSantiago()
    app.state._in_memory_logs = []  # cache conveniente
    # Lanzar tarea de background que monitorea métricas y emite alertas
    loop = asyncio.get_event_loop()
    app.state._alert_task = loop.create_task(_monitor_metrics_and_alert())


async def _monitor_metrics_and_alert():
    """Tarea de background que revisa métricas y escribe alertas en archivo si se exceden umbrales."""
    while True:
        try:
            await asyncio.sleep(ALERT_CHECK_INTERVAL)
            # Recalcular métricas
            from datetime import datetime

            logs = _read_logs(limit=1000)
            if not logs:
                continue
            count = len(logs)
            latencies = sorted([float(l.get("latency_seconds", 0)) for l in logs if l.get("latency_seconds") is not None])
            errors = sum(1 for l in logs if l.get("error"))
            # p95
            def _p(sorted_list, p):
                if not sorted_list:
                    return 0
                k = (len(sorted_list)-1) * (p/100)
                f = int(k)
                c = f + 1
                if c >= len(sorted_list):
                    return sorted_list[f]
                d0 = sorted_list[f] * (c-k)
                d1 = sorted_list[c] * (k-f)
                return d0 + d1

            p95 = _p(latencies, 95)
            error_rate = errors / count if count else 0

            alert = None
            if p95 > ALERT_P95_THRESHOLD:
                alert = {"timestamp": datetime.now().isoformat(), "type": "latency_p95", "p95": p95, "threshold": ALERT_P95_THRESHOLD}
            if error_rate > ALERT_ERROR_RATE_THRESHOLD:
                a = {"timestamp": datetime.now().isoformat(), "type": "error_rate", "error_rate": error_rate, "threshold": ALERT_ERROR_RATE_THRESHOLD}
                # prefer to combine alerts if both true
                if alert:
                    alert = {**alert, **a}
                else:
                    alert = a

            if alert:
                try:
                    with open(ALERTS_FILE, "a", encoding="utf-8") as f:
                        f.write(json.dumps(alert, ensure_ascii=False) + "\n")
                    logger.warning(f"ALERTA: {alert}")
                except Exception as e:
                    logger.error(f"No se pudo escribir alerta: {e}")

        except asyncio.CancelledError:
            break
        except Exception:
            # proteger el loop de errores
            logger.exception("Error en tarea de alertas")

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
    # Generar request_id y propagar al callback para correlación
    request_id = str(uuid4())
    try:
        if hasattr(agente, "callback") and hasattr(agente.callback, "current_request_id"):
            agente.callback.current_request_id = request_id

        respuesta = agente.procesar_consulta(q.query)

        # actualizar cache de logs leyendo la última entrada
        recent = _read_logs(limit=10)
        app.state._in_memory_logs = recent
        return {"response": respuesta, "request_id": request_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # limpiar request_id para evitar fugas entre peticiones
        try:
            if hasattr(agente, "callback") and hasattr(agente.callback, "current_request_id"):
                agente.callback.current_request_id = None
        except Exception:
            pass

@app.get("/api/logs")
def api_logs(limit: int = 100):
    logs = _read_logs(limit=limit)
    return {"count": len(logs), "logs": logs}


@app.get("/api/alerts")
def api_alerts(limit: int = 100):
    """Devuelve las últimas alertas generadas por el monitor interno."""
    if not ALERTS_FILE.exists():
        return {"count": 0, "alerts": []}
    lines = []
    with open(ALERTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                lines.append(json.loads(line))
            except Exception:
                continue
    return {"count": len(lines[-limit:]), "alerts": lines[-limit:]}

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


@app.get("/api/metrics/advanced")
def api_metrics_advanced(limit: int = 1000):
    """Métricas extendidas: percentiles (p50,p95,p99), throughput estimado y precisión básica.
    - Throughput: ejecuciones por segundo en el rango de logs devueltos
    - Precisión: si los logs contienen 'expected' y 'actual' se calcula exact match precision
    """
    import statistics
    from datetime import datetime

    logs = _read_logs(limit=limit)
    if not logs:
        return {"count": 0}

    count = len(logs)
    latencies = sorted([float(l.get("latency_seconds", 0)) for l in logs if l.get("latency_seconds") is not None])
    errors = sum(1 for l in logs if l.get("error"))

    # Percentiles
    def _percentile(sorted_list, p):
        if not sorted_list:
            return 0
        k = (len(sorted_list)-1) * (p/100)
        f = int(k)
        c = f + 1
        if c >= len(sorted_list):
            return sorted_list[f]
        d0 = sorted_list[f] * (c-k)
        d1 = sorted_list[c] * (k-f)
        return d0 + d1

    p50 = _percentile(latencies, 50)
    p95 = _percentile(latencies, 95)
    p99 = _percentile(latencies, 99)

    # Throughput: usar timestamps si existen
    timestamps = [l.get("timestamp") for l in logs if l.get("timestamp")]
    throughput = None
    if timestamps:
        try:
            times = [datetime.fromisoformat(ts) for ts in timestamps]
            duration = (max(times) - min(times)).total_seconds()
            throughput = count / duration if duration > 0 else count
        except Exception:
            throughput = None

    # Precisión básica (exact match) si hay expected/actual
    total_eval = 0
    correct = 0
    for l in logs:
        expected = l.get("expected")
        actual = l.get("actual")
        if expected is not None and actual is not None:
            total_eval += 1
            try:
                if str(expected).strip() == str(actual).strip():
                    correct += 1
            except Exception:
                pass

    precision = (correct / total_eval) if total_eval > 0 else None

    return {
        "count": count,
        "latency_avg": statistics.mean(latencies) if latencies else 0,
        "latency_max": max(latencies) if latencies else 0,
        "latency_p50": p50,
        "latency_p95": p95,
        "latency_p99": p99,
        "error_rate": errors / count if count else 0,
        "throughput_rps": throughput,
        "precision_exact_match": precision,
        "evaluated_examples": total_eval,
    }
