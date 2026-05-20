from __future__ import annotations

from typing import Any

import joblib
import numpy as np

from .features import FEATURE_COLUMNS, build_features


class TravelRecommender:
    def __init__(self, model_path: str):
        artifact = joblib.load(model_path)
        if isinstance(artifact, dict):
            self.model = artifact["model"]
            self.model_type = artifact.get("model_type", "sklearn")
            self.feature_columns = artifact.get("feature_columns", FEATURE_COLUMNS)
        else:
            self.model = artifact
            self.model_type = "sklearn"
            self.feature_columns = FEATURE_COLUMNS

    def predict(self, client: dict, programs: list[dict]) -> list[dict]:
        rows = [build_features(client, program) for program in programs]
        x = np.array([[row[col] for col in self.feature_columns] for row in rows], dtype=np.float32)
        scores = self.model.predict(x)
        scores = np.clip(np.asarray(scores, dtype=float).reshape(-1), 0.0, 1.0)
        ranked = []
        for program, score in zip(programs, scores):
            item = dict(program)
            item["score"] = round(float(score), 4)
            ranked.append(item)
        return sorted(ranked, key=lambda item: item["score"], reverse=True)
