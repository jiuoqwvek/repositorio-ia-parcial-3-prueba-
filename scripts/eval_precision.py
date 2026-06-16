"""
Herramienta de evaluación de precisión basada en los logs JSONL.

Uso:
  python scripts/eval_precision.py --file ./logs/agent_logs.jsonl

Calcula métricas básicas (exact-match precision, recall, f1) y un breakdown por herramienta.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path


def load_logs(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Logs file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def evaluate(logs):
    # Count TP/FP/FN using exact match between 'expected' and 'actual'
    total = 0
    correct = 0
    per_tool = defaultdict(lambda: {"total": 0, "correct": 0})

    for l in logs:
        expected = l.get("expected")
        actual = l.get("actual")
        tool = l.get("tool_name", "unknown")
        if expected is None or actual is None:
            continue
        total += 1
        per_tool[tool]["total"] += 1
        try:
            if str(expected).strip() == str(actual).strip():
                correct += 1
                per_tool[tool]["correct"] += 1
        except Exception:
            continue

    precision = (correct / total) if total > 0 else None
    # For exact-match both precision and recall collapse to same value when using logs as eval set
    recall = precision
    f1 = (2 * precision * recall / (precision + recall)) if precision else None

    return {
        "evaluated": total,
        "correct": correct,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "per_tool": per_tool,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", default="./logs/agent_logs.jsonl", help="Ruta al archivo JSONL de logs")
    args = p.parse_args()

    path = Path(args.file)
    logs = list(load_logs(path))
    res = evaluate(logs)

    print("Evaluación de precisión (exact-match)")
    print("--------------------------------")
    print(f"Ejemplos evaluados: {res['evaluated']}")
    print(f"Correctos: {res['correct']}")
    print(f"Precision: {res['precision']}")
    print(f"Recall: {res['recall']}")
    print(f"F1: {res['f1']}")
    print("\nDesglose por herramienta:")
    for tool, stats in res["per_tool"].items():
        total = stats["total"]
        correct = stats["correct"]
        pct = (correct / total) if total > 0 else None
        print(f" - {tool}: {correct}/{total} (accuracy: {pct})")


if __name__ == "__main__":
    main()
