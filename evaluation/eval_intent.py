"""
Intent Classification Evaluation
Runs test messages through the keyword-based classifier and computes:
  - Accuracy, Precision, Recall, F1 (macro)
  - Confusion matrix
  - Per-class breakdown

Usage:
    python evaluation/eval_intent.py
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Inline copy of the classifier (avoids importing FastAPI / Redis at eval time)
# ---------------------------------------------------------------------------

def classify_intent(content: str) -> str:
    content_lower = content.lower()

    # Exact copy of conversations.py _classify_intent keywords
    recommendation_keywords = [
        "recommand", "suggest", "conseil", "meilleur", "proposer",
        "personnalis", "adapt\u00e9", "pour moi", "quel voyage",
        "quelque chose", "selon mon profil",
        "\u062a\u0648\u0635\u064a\u0629", "\u0627\u0642\u062a\u0631\u0627\u062d",
        "\u0623\u0641\u0636\u0644", "\u0627\u0646\u0635\u062d\u0646\u064a",
        "\u0627\u0642\u062a\u0631\u062d",
    ]
    passport_keywords = [
        "passeport", "passport",
        "\u062c\u0648\u0627\u0632", "visa",
    ]
    booking_keywords = [
        "r\u00e9serv", "reserv", "book",
        "\u062d\u062c\u0632", "inscrire",
    ]
    program_keywords = [
        "programme", "forfait", "s\u00e9jour", "voyage",
        "offre", "package", "formule", "circuit", "disponible",
        "avez-vous", "proposez", "prix pour", "combien pour",
        "\u0628\u0631\u0646\u0627\u0645\u062c", "\u0628\u0631\u0627\u0645\u062c",
        "\u0631\u062d\u0644\u0629", "\u0639\u0631\u0636", "\u0639\u0631\u0648\u0636",
        "\u0628\u0627\u0642\u0629",
    ]

    for kw in recommendation_keywords:
        if kw in content_lower:
            return "recommendation"
    for kw in passport_keywords:
        if kw in content_lower:
            return "passport"
    for kw in booking_keywords:
        if kw in content_lower:
            return "booking"
    for kw in program_keywords:
        if kw in content_lower:
            return "program"
    return "general"


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

CLASSES = ["recommendation", "program", "booking", "passport", "general"]


def compute_metrics(y_true: list, y_pred: list) -> dict:
    labels = CLASSES
    n = len(labels)
    label_idx = {l: i for i, l in enumerate(labels)}

    cm = np.zeros((n, n), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[label_idx.get(t, 0)][label_idx.get(p, 0)] += 1

    accuracy = sum(t == p for t, p in zip(y_true, y_pred)) / len(y_true)

    per_class = {}
    for i, cls in enumerate(labels):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec  = tp / (tp + fn) if (tp + fn) else 0.0
        f1   = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        per_class[cls] = {"precision": prec, "recall": rec, "f1": f1, "support": int(cm[i].sum())}

    macro_prec = np.mean([per_class[c]["precision"] for c in labels])
    macro_rec  = np.mean([per_class[c]["recall"]    for c in labels])
    macro_f1   = np.mean([per_class[c]["f1"]        for c in labels])

    return {
        "accuracy": accuracy,
        "macro_precision": macro_prec,
        "macro_recall": macro_rec,
        "macro_f1": macro_f1,
        "per_class": per_class,
        "confusion_matrix": cm,
    }


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

def save_confusion_matrix(cm, labels, out_dir):
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=10)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Predit", fontsize=11)
    ax.set_ylabel("Reel", fontsize=11)
    ax.set_title("Matrice de Confusion - Classification d'Intention", fontsize=13)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() * 0.5 else "black", fontsize=12)
    plt.colorbar(im, ax=ax)
    plt.tight_layout()
    path = out_dir / "intent_confusion_matrix.png"
    fig.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


def save_per_class_chart(per_class, out_dir):
    labels = list(per_class.keys())
    prec   = [per_class[c]["precision"] for c in labels]
    rec    = [per_class[c]["recall"]    for c in labels]
    f1     = [per_class[c]["f1"]        for c in labels]

    x = np.arange(len(labels))
    width = 0.25
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width, prec, width, label="Precision", color="#4C72B0")
    ax.bar(x,         rec,  width, label="Recall",    color="#55A868")
    ax.bar(x + width, f1,   width, label="F1",        color="#C44E52")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Score", fontsize=11)
    ax.set_title("Metriques par Classe - Classification d'Intention", fontsize=13)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    path = out_dir / "intent_per_class.png"
    fig.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    base = Path(__file__).parent
    data_path = base / "data" / "intent_test_set.json"
    out_dir   = base / "results"
    out_dir.mkdir(exist_ok=True)

    with open(data_path, encoding="utf-8") as f:
        test_set = json.load(f)

    y_true, y_pred = [], []
    errors = []

    print(f"\n{'='*55}")
    print("  Rihla-AI -- Evaluation Classification d'Intention")
    print(f"{'='*55}\n")

    for item in test_set:
        msg      = item["message"]
        expected = item["expected"]
        predicted = classify_intent(msg)
        y_true.append(expected)
        y_pred.append(predicted)
        ok = "OK" if predicted == expected else "XX"
        if predicted != expected:
            errors.append({**item, "predicted": predicted})
        safe_msg = msg[:50].encode("ascii", "replace").decode()
        print(f"  [{ok}] #{item['id']:02d} | expected={expected:<18} predicted={predicted:<18} | {safe_msg}")

    metrics = compute_metrics(y_true, y_pred)

    print(f"\n{'-'*55}")
    print(f"  Accuracy         : {metrics['accuracy']:.1%}")
    print(f"  Macro Precision  : {metrics['macro_precision']:.1%}")
    print(f"  Macro Recall     : {metrics['macro_recall']:.1%}")
    print(f"  Macro F1         : {metrics['macro_f1']:.1%}")
    print(f"{'-'*55}")
    print(f"\n  Par classe:")
    for cls, m in metrics["per_class"].items():
        print(f"    {cls:<18} P={m['precision']:.2f}  R={m['recall']:.2f}  F1={m['f1']:.2f}  (n={m['support']})")

    if errors:
        print(f"\n  Erreurs ({len(errors)}):")
        for e in errors:
            safe_e = e["message"][:60].encode("ascii", "replace").decode()
            print(f"    #{e['id']} expected={e['expected']} predicted={e['predicted']} | {safe_e}")

    # Save charts
    print("\n  Generation des graphiques...")
    save_confusion_matrix(metrics["confusion_matrix"], CLASSES, out_dir)
    save_per_class_chart(metrics["per_class"], out_dir)

    # Save JSON results
    results = {
        "accuracy":         round(float(metrics["accuracy"]), 4),
        "macro_precision":  round(float(metrics["macro_precision"]), 4),
        "macro_recall":     round(float(metrics["macro_recall"]), 4),
        "macro_f1":         round(float(metrics["macro_f1"]), 4),
        "per_class":        {c: {k: round(float(v), 4) if isinstance(v, float) else v
                                 for k, v in m.items()}
                             for c, m in metrics["per_class"].items()},
        "errors":           errors,
        "n_samples":        len(test_set),
    }
    json_path = out_dir / "intent_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {json_path}")
    print(f"\n{'='*55}\n")

    return results


if __name__ == "__main__":
    main()
