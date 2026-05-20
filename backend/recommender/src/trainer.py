from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupShuffleSplit
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from .evaluate import (
    regression_metrics,
    save_confusion_matrix_plot,
    save_error_distribution,
    save_feature_importance,
    save_learning_curve,
    save_metric_bars,
    save_ndcg_comparison,
    save_ndcg_curve,
    save_prediction_scatter,
    save_residual_plot,
)
from .features import FEATURE_COLUMNS, make_training_frame


@dataclass
class Paths:
    root: Path

    @property
    def data(self) -> Path:
        return self.root / "data"

    @property
    def models(self) -> Path:
        return self.root / "models"

    @property
    def reports(self) -> Path:
        return self.root / "reports"


PROGRAMS = [
    {"id": 1, "title_fr": "Istanbul Découverte - Budget", "destination": "Istanbul", "price": 2100, "duration_days": 7, "category": "budget", "target_audience": "student", "visa_required": False, "hotel_stars": 2, "climate": "Méditerranéen", "best_season": "Printemps, Automne", "amenities": ["wifi", "petit-dejeuner"], "includes": ["vol aller-retour", "hotel 6 nuits", "visites"]},
    {"id": 2, "title_fr": "Istanbul Premium - Business", "destination": "Istanbul", "price": 5200, "duration_days": 7, "category": "luxury", "target_audience": "business", "visa_required": False, "hotel_stars": 5, "climate": "Méditerranéen", "best_season": "Printemps, Automne", "amenities": ["wifi", "spa", "business center"], "includes": ["vol aller-retour", "transfert prive", "hotel 5 etoiles"]},
    {"id": 3, "title_fr": "Dubai Aventure", "destination": "Dubai", "price": 3200, "duration_days": 7, "category": "adventure", "target_audience": "young", "visa_required": True, "hotel_stars": 4, "climate": "Désertique", "best_season": "Hiver, Printemps", "amenities": ["wifi", "piscine"], "includes": ["vol aller-retour", "desert safari", "city tour"]},
    {"id": 4, "title_fr": "Dubai Royal Experience", "destination": "Dubai", "price": 11500, "duration_days": 7, "category": "luxury", "target_audience": "couple", "visa_required": True, "hotel_stars": 5, "climate": "Désertique", "best_season": "Hiver, Printemps", "amenities": ["spa", "piscine", "plage"], "includes": ["vol business", "hotel palace", "diner romantique"]},
    {"id": 5, "title_fr": "Paris en Famille", "destination": "Paris", "price": 4800, "duration_days": 7, "category": "standard", "target_audience": "family", "visa_required": True, "hotel_stars": 3, "climate": "Océanique", "best_season": "Printemps, Été", "amenities": ["wifi", "petit-dejeuner"], "includes": ["vol aller-retour", "hotel familial", "disney option"]},
    {"id": 6, "title_fr": "Omra Complète 15 jours", "destination": "La Mecque", "price": 6200, "duration_days": 15, "category": "religious", "target_audience": "all", "visa_required": True, "hotel_stars": 4, "climate": "Désertique", "best_season": "Toute l'année", "amenities": ["wifi", "proche haram"], "includes": ["vol aller-retour", "visa omra", "transferts"]},
    {"id": 7, "title_fr": "Marrakech Authentique", "destination": "Marrakech", "price": 2600, "duration_days": 7, "category": "standard", "target_audience": "all", "visa_required": False, "hotel_stars": 4, "climate": "Semi-aride", "best_season": "Printemps, Automne", "amenities": ["wifi", "piscine", "spa"], "includes": ["vol aller-retour", "riad", "excursions"]},
    {"id": 8, "title_fr": "Antalya Tout Inclus - Famille", "destination": "Antalya", "price": 2800, "duration_days": 7, "category": "standard", "target_audience": "family", "visa_required": False, "hotel_stars": 4, "climate": "Méditerranéen", "best_season": "Été, Automne", "amenities": ["piscine", "plage", "wifi"], "includes": ["vol aller-retour", "hotel", "tout inclus"]},
    {"id": 9, "title_fr": "Antalya Prestige", "destination": "Antalya", "price": 4500, "duration_days": 7, "category": "luxury", "target_audience": "couple", "visa_required": False, "hotel_stars": 5, "climate": "Méditerranéen", "best_season": "Été, Automne", "amenities": ["spa", "piscine", "plage"], "includes": ["vol aller-retour", "resort luxe", "tout inclus"]},
    {"id": 10, "title_fr": "Le Caire & Pyramides", "destination": "Le Caire", "price": 2100, "duration_days": 7, "category": "budget", "target_audience": "all", "visa_required": True, "hotel_stars": 3, "climate": "Désertique", "best_season": "Hiver, Printemps", "amenities": ["wifi", "petit-dejeuner"], "includes": ["vol aller-retour", "pyramides", "musee"]},
    {"id": 11, "title_fr": "Rome Éternelle", "destination": "Rome", "price": 2400, "duration_days": 5, "category": "standard", "target_audience": "all", "visa_required": True, "hotel_stars": 3, "climate": "Méditerranéen", "best_season": "Printemps, Automne", "amenities": ["wifi", "petit-dejeuner"], "includes": ["vol aller-retour", "hotel centre", "city pass"]},
]


class TorchMLPRegressor:
    def __init__(self, input_dim: int, epochs: int = 50, seed: int = 42):
        self.input_dim = input_dim
        self.epochs = epochs
        self.seed = seed
        self.history: dict[str, list[float]] = {"train_loss": []}
        self.model = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )
        self.mean_: np.ndarray | None = None
        self.std_: np.ndarray | None = None

    def fit(self, x: np.ndarray, y: np.ndarray) -> "TorchMLPRegressor":
        torch.manual_seed(self.seed)
        self.mean_ = x.mean(axis=0)
        self.std_ = x.std(axis=0)
        self.std_[self.std_ == 0] = 1.0
        x_scaled = (x - self.mean_) / self.std_
        dataset = TensorDataset(torch.tensor(x_scaled, dtype=torch.float32), torch.tensor(y.reshape(-1, 1), dtype=torch.float32))
        loader = DataLoader(dataset, batch_size=128, shuffle=True)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        loss_fn = nn.MSELoss()
        self.model.train()
        for _ in range(self.epochs):
            losses = []
            for xb, yb in loader:
                optimizer.zero_grad()
                loss = loss_fn(self.model(xb), yb)
                loss.backward()
                optimizer.step()
                losses.append(float(loss.detach()))
            self.history["train_loss"].append(float(np.mean(losses)))
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        if self.mean_ is None or self.std_ is None:
            raise RuntimeError("TorchMLPRegressor must be fitted before prediction.")
        x_scaled = (x - self.mean_) / self.std_
        self.model.eval()
        with torch.no_grad():
            return self.model(torch.tensor(x_scaled, dtype=torch.float32)).numpy().reshape(-1)


def save_scraped_data(paths: Paths) -> None:
    scraped = [
        {"source": "TTS Booking", "url": "https://www.ttsbooking.tn/voyages-organises/", "destination": "Istanbul", "price_tnd": 2005, "duration_days": 7, "category": "standard", "target": "all", "notes": "Istanbul Juin 2026, vol Turkish Airlines"},
        {"source": "TTS Booking", "url": "https://www.ttsbooking.tn/voyages-organises/", "destination": "Istanbul", "price_tnd": 2505, "duration_days": 7, "category": "standard", "target": "young", "notes": "Istanbul Summer 2026"},
        {"source": "TTS Booking", "url": "https://www.ttsbooking.tn/voyages-organises/", "destination": "Antalya", "price_tnd": 3790, "duration_days": 8, "category": "standard", "target": "family", "notes": "Antalya Istanbul Summer 2026"},
        {"source": "VoyageTunisie", "url": "https://www.voyagetunisie.tn/voyages-de-noces/istanbul.html", "destination": "Istanbul", "price_tnd": 1000, "duration_days": 7, "category": "budget", "target": "couple", "notes": "Voyage de noces Istanbul à partir de 1000 TND"},
        {"source": "CTE", "url": "https://www.cte.tn/voyage/voyage-istanbul-2026.html", "destination": "Istanbul", "price_tnd": 1990, "duration_days": 7, "category": "standard", "target": "all", "notes": "Voyage organisé Istanbul 2026 avec excursions"},
        {"source": "Miralina Travel", "url": "https://www.hotelstunisie.tn/voyages", "destination": "Antalya", "price_tnd": 1500, "duration_days": 8, "category": "budget", "target": "family", "notes": "Vol, transfert, hébergement"},
        {"source": "Miralina Travel", "url": "https://www.hotelstunisie.tn/voyages", "destination": "Istanbul", "price_tnd": 1500, "duration_days": 7, "category": "budget", "target": "all", "notes": "Vol, transfert, hébergement"},
        {"source": "Omra24", "url": "https://www.omra24.com/", "destination": "La Mecque", "price_tnd": 3000, "duration_days": 14, "category": "religious", "target": "all", "notes": "Omra 2 semaines, fourchette basse chambre quadruple"},
        {"source": "OmraTunisie", "url": "https://www.omratunisie.tn/omra/sup.html", "destination": "La Mecque", "price_tnd": 5500, "duration_days": 14, "category": "religious", "target": "all", "notes": "Omra deux semaines, chambre double"},
        {"source": "Tunisie Promo", "url": "https://tp.octasoft.com.tn/", "destination": "La Mecque", "price_tnd": 4050, "duration_days": 15, "category": "religious", "target": "all", "notes": "OMRA 15 jours / 14 nuits"},
    ]
    enrichment = {
        "Dubai": {"activities": ["desert safari", "Burj Khalifa", "shopping"], "amenities": ["piscine", "spa", "plage"], "season": "Hiver, Printemps"},
        "Paris": {"activities": ["Disneyland", "Louvre", "tour Eiffel"], "amenities": ["wifi", "petit-dejeuner"], "season": "Printemps, Été"},
        "Marrakech": {"activities": ["Jemaa el-Fna", "jardin Majorelle", "excursion Atlas"], "amenities": ["riad", "piscine", "spa"], "season": "Printemps, Automne"},
        "Le Caire": {"activities": ["pyramides", "musée égyptien", "croisière Nil"], "amenities": ["wifi", "petit-dejeuner"], "season": "Hiver, Printemps"},
        "Rome": {"activities": ["Colisée", "Vatican", "fontaine de Trevi"], "amenities": ["wifi", "centre-ville"], "season": "Printemps, Automne"},
    }
    scraped_dir = paths.data / "scraped"
    scraped_dir.mkdir(parents=True, exist_ok=True)
    (scraped_dir / "public_travel_offers.json").write_text(json.dumps(scraped, ensure_ascii=False, indent=2), encoding="utf-8")
    (scraped_dir / "destination_enrichment.json").write_text(json.dumps(enrichment, ensure_ascii=False, indent=2), encoding="utf-8")


def generate_clients(n: int = 650, seed: int = 42) -> list[dict[str, Any]]:
    random.seed(seed)
    profiles = ["student", "young", "family", "couple", "business", "senior"]
    budget_by_profile = {
        "student": ["budget", "budget", "standard"],
        "young": ["budget", "standard", "standard", "luxury"],
        "family": ["standard", "standard", "budget", "luxury"],
        "couple": ["standard", "luxury", "budget"],
        "business": ["standard", "luxury", "luxury"],
        "senior": ["budget", "standard", "standard"],
    }
    clients = []
    for idx in range(n):
        profile = random.choice(profiles)
        clients.append({
            "id": f"C{idx + 1:04d}",
            "profile_type": profile,
            "budget_preference": random.choice(budget_by_profile[profile]),
            "preferred_language": random.choices(["fr", "ar"], weights=[0.72, 0.28])[0],
        })
    return clients


def prepare_data(paths: Paths) -> pd.DataFrame:
    save_scraped_data(paths)
    clients = generate_clients()
    synthetic_dir = paths.data / "synthetic"
    training_dir = paths.data / "training"
    synthetic_dir.mkdir(parents=True, exist_ok=True)
    training_dir.mkdir(parents=True, exist_ok=True)
    (synthetic_dir / "clients.json").write_text(json.dumps(clients, ensure_ascii=False, indent=2), encoding="utf-8")
    (synthetic_dir / "programs.json").write_text(json.dumps(PROGRAMS, ensure_ascii=False, indent=2), encoding="utf-8")
    frame = make_training_frame(clients, PROGRAMS)
    frame.to_csv(training_dir / "training_dataset.csv", index=False, encoding="utf-8")
    return frame


def train_all(root: Path) -> pd.DataFrame:
    paths = Paths(root)
    paths.models.mkdir(parents=True, exist_ok=True)
    paths.reports.mkdir(parents=True, exist_ok=True)
    frame = prepare_data(paths)

    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(splitter.split(frame, groups=frame["client_id"]))
    train, test = frame.iloc[train_idx], frame.iloc[test_idx]
    x_train = train[FEATURE_COLUMNS].to_numpy(dtype=np.float32)
    y_train = train["label"].to_numpy(dtype=np.float32)
    x_test = test[FEATURE_COLUMNS].to_numpy(dtype=np.float32)
    y_test = test["label"].to_numpy(dtype=np.float32)
    groups = test["client_id"].to_numpy()

    candidates = [
        ("LightGBM", lgb.LGBMRegressor(objective="regression", n_estimators=500, learning_rate=0.05, max_depth=6, num_leaves=63, random_state=42, verbosity=-1), "lightgbm_recommender.joblib"),
        ("Random Forest", RandomForestRegressor(n_estimators=300, max_depth=8, min_samples_leaf=10, random_state=42, n_jobs=1), "rf_recommender.joblib"),
        ("Neural Network", TorchMLPRegressor(input_dim=len(FEATURE_COLUMNS), epochs=50), "mlp_recommender.joblib"),
    ]

    results: list[dict[str, Any]] = []
    predictions_by_model: dict[str, np.ndarray] = {}
    sample_x = x_test[:11]
    for name, model, filename in candidates:
        start = time.perf_counter()
        model.fit(x_train, y_train)
        train_seconds = time.perf_counter() - start
        predictions = np.clip(model.predict(x_test), 0, 1)
        predictions_by_model[name] = predictions
        infer_start = time.perf_counter()
        _ = model.predict(sample_x)
        infer_ms = (time.perf_counter() - infer_start) * 1000
        row = {"model": name, **regression_metrics(y_test, predictions, groups), "train_seconds": train_seconds, "inference_ms_11_programs": infer_ms}
        results.append(row)
        joblib.dump({"model": model, "model_type": "torch_mlp" if name == "Neural Network" else "sklearn", "feature_columns": FEATURE_COLUMNS, "metrics": row}, paths.models / filename)

        safe_name = name.lower().replace(" ", "_")
        save_confusion_matrix_plot(y_test, predictions, f"Matrice de confusion - {name}", paths.reports / f"confusion_matrix_{safe_name}.png")
        save_prediction_scatter(y_test, predictions, f"Score réel vs prédit - {name}", paths.reports / f"predicted_vs_actual_{safe_name}.png")
        save_residual_plot(y_test, predictions, f"Analyse des résidus - {name}", paths.reports / f"residuals_{safe_name}.png")
        save_error_distribution(y_test, predictions, f"Distribution des erreurs - {name}", paths.reports / f"error_distribution_{safe_name}.png")

        if name == "LightGBM":
            save_feature_importance(FEATURE_COLUMNS, model.feature_importances_, "LightGBM feature importance", paths.reports / "feature_importance_lightgbm.png")
        if name == "Random Forest":
            save_feature_importance(FEATURE_COLUMNS, model.feature_importances_, "Random Forest feature importance", paths.reports / "feature_importance_rf.png")
        if name == "Neural Network":
            save_learning_curve(model.history, paths.reports / "learning_curve_mlp.png")

    metrics = pd.DataFrame(results).sort_values(["NDCG@5", "RMSE"], ascending=[False, True])
    metrics.to_csv(paths.reports / "metrics_comparison.csv", index=False)
    save_ndcg_comparison(results, paths.reports / "ndcg5_comparison.png")
    save_metric_bars(results, ["RMSE", "MAE"], paths.reports / "rmse_mae_comparison.png")
    save_metric_bars(results, ["train_seconds", "inference_ms_11_programs"], paths.reports / "time_comparison.png")
    save_ndcg_curve(predictions_by_model, y_test, groups, paths.reports / "ndcg_at_k_curve.png")
    return metrics
