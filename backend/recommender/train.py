from __future__ import annotations

from pathlib import Path

from src.trainer import train_all


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    metrics = train_all(root)
    print("\n=== Comparaison des modèles ===")
    print(metrics.to_string(index=False))
