from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, mean_absolute_error, mean_squared_error


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def ndcg_at_k(y_true: np.ndarray, y_pred: np.ndarray, groups: np.ndarray, k: int) -> float:
    scores = []
    for group in np.unique(groups):
        mask = groups == group
        true_group = y_true[mask]
        pred_group = y_pred[mask]
        order = np.argsort(pred_group)[::-1][:k]
        ideal = np.argsort(true_group)[::-1][:k]
        dcg = sum((2 ** true_group[i] - 1) / np.log2(rank + 2) for rank, i in enumerate(order))
        idcg = sum((2 ** true_group[i] - 1) / np.log2(rank + 2) for rank, i in enumerate(ideal))
        scores.append(dcg / idcg if idcg > 0 else 0.0)
    return float(np.mean(scores))


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray, groups: np.ndarray) -> dict[str, float]:
    return {
        "RMSE": rmse(y_true, y_pred),
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "NDCG@3": ndcg_at_k(y_true, y_pred, groups, 3),
        "NDCG@5": ndcg_at_k(y_true, y_pred, groups, 5),
    }


def save_feature_importance(names: list[str], values: np.ndarray, title: str, path: Path) -> None:
    order = np.argsort(values)[-15:]
    plt.figure(figsize=(9, 6))
    plt.barh(np.array(names)[order], values[order])
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def save_learning_curve(history: dict[str, list[float]], path: Path) -> None:
    plt.figure(figsize=(8, 5))
    for name, values in history.items():
        plt.plot(values, label=name)
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def save_ndcg_comparison(metrics: list[dict[str, Any]], path: Path) -> None:
    frame = pd.DataFrame(metrics)
    plt.figure(figsize=(7, 5))
    plt.bar(frame["model"], frame["NDCG@5"])
    plt.ylim(0, 1.05)
    plt.ylabel("NDCG@5")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def relevance_classes(values: np.ndarray) -> np.ndarray:
    """Convert continuous recommendation scores into report-friendly classes."""
    bins = [0.0, 0.50, 0.75, 1.01]
    return np.digitize(values, bins, right=False) - 1


def save_confusion_matrix_plot(y_true: np.ndarray, y_pred: np.ndarray, title: str, path: Path) -> None:
    labels = ["faible", "moyen", "élevé"]
    matrix = confusion_matrix(relevance_classes(y_true), relevance_classes(y_pred), labels=[0, 1, 2])
    plt.figure(figsize=(6, 5))
    plt.imshow(matrix, cmap="Blues")
    plt.title(title)
    plt.xlabel("Classe prédite")
    plt.ylabel("Classe réelle")
    plt.xticks(range(len(labels)), labels)
    plt.yticks(range(len(labels)), labels)
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            plt.text(col, row, str(matrix[row, col]), ha="center", va="center", color="black")
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def save_prediction_scatter(y_true: np.ndarray, y_pred: np.ndarray, title: str, path: Path) -> None:
    plt.figure(figsize=(6, 6))
    plt.scatter(y_true, y_pred, alpha=0.45, s=18)
    plt.plot([0, 1], [0, 1], color="black", linewidth=1)
    plt.xlabel("Score réel")
    plt.ylabel("Score prédit")
    plt.title(title)
    plt.xlim(0, 1.02)
    plt.ylim(0, 1.02)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def save_residual_plot(y_true: np.ndarray, y_pred: np.ndarray, title: str, path: Path) -> None:
    residuals = y_true - y_pred
    plt.figure(figsize=(7, 5))
    plt.scatter(y_pred, residuals, alpha=0.45, s=18)
    plt.axhline(0, color="black", linewidth=1)
    plt.xlabel("Score prédit")
    plt.ylabel("Résidu réel - prédit")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def save_error_distribution(y_true: np.ndarray, y_pred: np.ndarray, title: str, path: Path) -> None:
    errors = np.abs(y_true - y_pred)
    plt.figure(figsize=(7, 5))
    plt.hist(errors, bins=24, color="#4C78A8", edgecolor="white")
    plt.xlabel("Erreur absolue")
    plt.ylabel("Nombre d'exemples")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def save_metric_bars(metrics: list[dict[str, Any]], metric_names: list[str], path: Path) -> None:
    frame = pd.DataFrame(metrics)
    x = np.arange(len(frame["model"]))
    width = 0.8 / len(metric_names)
    plt.figure(figsize=(9, 5))
    for idx, metric in enumerate(metric_names):
        plt.bar(x + idx * width, frame[metric], width=width, label=metric)
    plt.xticks(x + width * (len(metric_names) - 1) / 2, frame["model"])
    plt.ylabel("Valeur")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def save_ndcg_curve(predictions_by_model: dict[str, np.ndarray], y_true: np.ndarray, groups: np.ndarray, path: Path) -> None:
    ks = [1, 2, 3, 4, 5]
    plt.figure(figsize=(8, 5))
    for model_name, y_pred in predictions_by_model.items():
        plt.plot(ks, [ndcg_at_k(y_true, y_pred, groups, k) for k in ks], marker="o", label=model_name)
    plt.xlabel("k")
    plt.ylabel("NDCG@k")
    plt.ylim(0, 1.05)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
