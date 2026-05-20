"""
Master Evaluation Runner
Runs all Rihla-AI evaluation modules and generates a summary report.

Usage:
    python evaluation/run_all.py [--host http://localhost:8000] [--skip-rag] [--skip-latency]

Outputs (in evaluation/results/):
    intent_results.json        + intent_confusion_matrix.png + intent_per_class.png
    rag_results.json           + rag_by_category.png         + rag_latency.png
    latency_results.json       + latency_by_module.png
    summary_dashboard.png      ← combined overview chart
    evaluation_report.json     ← consolidated results
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# Add project root to path so modules can import each other
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "backend"))

# ---------------------------------------------------------------------------
# Import sub-evaluators
# ---------------------------------------------------------------------------

def run_intent() -> dict:
    print("\n" + "="*60)
    print("  [1/3] Classification d'Intention")
    print("="*60)
    from evaluation.eval_intent import main as intent_main
    return intent_main()


def run_rag(host: str) -> dict:
    print("\n" + "="*60)
    print("  [2/3] RAG")
    print("="*60)
    import sys as _sys
    _sys.argv = ["eval_rag.py", "--host", host, "--client", "eval_master_rag"]
    from evaluation.eval_rag import main as rag_main
    return rag_main()


def run_latency(host: str, n: int = 2) -> dict:
    print("\n" + "="*60)
    print("  [3/3] Latence")
    print("="*60)
    import sys as _sys
    _sys.argv = ["eval_latency.py", "--host", host, "--n", str(n)]
    from evaluation.eval_latency import main as lat_main
    return lat_main()


# ---------------------------------------------------------------------------
# Summary dashboard chart
# ---------------------------------------------------------------------------

def save_summary_dashboard(intent_r: dict, rag_r: dict | None, lat_r: dict | None, out_dir: Path):
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle("Rihla-AI — Tableau de Bord d'Évaluation", fontsize=16, fontweight="bold", y=0.98)
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.4)

    # ── 1. Intent global metrics (bar)
    ax1 = fig.add_subplot(gs[0, 0])
    metrics = ["Accuracy", "Precision\n(macro)", "Recall\n(macro)", "F1\n(macro)"]
    values  = [
        intent_r["accuracy"],
        intent_r["macro_precision"],
        intent_r["macro_recall"],
        intent_r["macro_f1"],
    ]
    colors = ["#4C72B0" if v >= 0.8 else "#C44E52" for v in values]
    bars = ax1.bar(metrics, values, color=colors)
    ax1.set_ylim(0, 1.15)
    ax1.set_title("Intent — Métriques globales", fontsize=11)
    ax1.set_ylabel("Score")
    for bar, v in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width()/2, v + 0.02, f"{v:.1%}", ha="center", fontsize=9)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    # ── 2. Intent per-class F1
    ax2 = fig.add_subplot(gs[0, 1])
    classes = list(intent_r["per_class"].keys())
    f1s     = [intent_r["per_class"][c]["f1"] for c in classes]
    clr2    = ["#4C72B0" if v >= 0.8 else "#C44E52" for v in f1s]
    ax2.barh(classes, f1s, color=clr2)
    ax2.set_xlim(0, 1.1)
    ax2.set_title("Intent — F1 par classe", fontsize=11)
    ax2.set_xlabel("F1")
    ax2.grid(axis="x", linestyle="--", alpha=0.4)
    for i, v in enumerate(f1s):
        ax2.text(v + 0.01, i, f"{v:.2f}", va="center", fontsize=9)

    # ── 3. RAG metrics
    ax3 = fig.add_subplot(gs[0, 2])
    if rag_r:
        rag_metrics = ["Answer\nRelevance", "Exact Match\nRate"]
        rag_vals    = [rag_r["avg_relevance"], rag_r["exact_match_rate"]]
        rclr        = ["#4C72B0" if v >= 0.6 else "#C44E52" for v in rag_vals]
        bars3 = ax3.bar(rag_metrics, rag_vals, color=rclr, width=0.4)
        ax3.set_ylim(0, 1.15)
        ax3.set_title(f"RAG — Métriques globales\n({rag_r['n_success']}/{rag_r['n_total']} requêtes)", fontsize=11)
        ax3.set_ylabel("Score")
        for bar, v in zip(bars3, rag_vals):
            ax3.text(bar.get_x() + bar.get_width()/2, v + 0.02, f"{v:.1%}", ha="center", fontsize=9)
        ax3.grid(axis="y", linestyle="--", alpha=0.4)
    else:
        ax3.text(0.5, 0.5, "RAG non exécuté\n(--skip-rag)", ha="center", va="center",
                 transform=ax3.transAxes, fontsize=12, color="gray")
        ax3.set_title("RAG — Métriques globales", fontsize=11)

    # ── 4. RAG by category relevance
    ax4 = fig.add_subplot(gs[1, 0])
    if rag_r and rag_r.get("by_category"):
        cats = sorted(rag_r["by_category"].keys())
        rels = [rag_r["by_category"][c]["avg_relevance"] for c in cats]
        ax4.barh(cats, rels, color="#55A868")
        ax4.set_xlim(0, 1.1)
        ax4.set_title("RAG — Relevance par catégorie", fontsize=11)
        ax4.set_xlabel("Answer Relevance")
        ax4.grid(axis="x", linestyle="--", alpha=0.4)
    else:
        ax4.text(0.5, 0.5, "N/A", ha="center", va="center", transform=ax4.transAxes, color="gray")
        ax4.set_title("RAG — Relevance par catégorie", fontsize=11)

    # ── 5. Latency by module
    ax5 = fig.add_subplot(gs[1, 1])
    if lat_r:
        mods  = list(lat_r.keys())
        means = [lat_r[m]["mean_ms"] for m in mods]
        short_mods = [m.replace("RAG — ", "RAG\n") for m in mods]
        ax5.barh(short_mods, means, color="#DD8452")
        ax5.set_title("Latence moyenne par module (ms)", fontsize=11)
        ax5.set_xlabel("ms")
        ax5.grid(axis="x", linestyle="--", alpha=0.4)
        for i, v in enumerate(means):
            ax5.text(v + 10, i, f"{v:.0f}ms", va="center", fontsize=8)
    else:
        ax5.text(0.5, 0.5, "Latence non mesurée\n(--skip-latency)", ha="center", va="center",
                 transform=ax5.transAxes, fontsize=12, color="gray")
        ax5.set_title("Latence par module", fontsize=11)

    # ── 6. Score summary table
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.axis("off")
    rows = [
        ["Module", "Métrique", "Score"],
        ["Intent", "Accuracy",   f"{intent_r['accuracy']:.1%}"],
        ["Intent", "Macro F1",   f"{intent_r['macro_f1']:.1%}"],
    ]
    if rag_r:
        rows += [
            ["RAG",    "Answer Rel.", f"{rag_r['avg_relevance']:.1%}"],
            ["RAG",    "Exact Match", f"{rag_r['exact_match_rate']:.1%}"],
            ["RAG",    "Lat. moy.",   f"{rag_r['avg_latency_ms']:.0f}ms"],
        ]
    if lat_r:
        rag_mods = [m for m in lat_r if "RAG" in m]
        if rag_mods:
            avg_rag_lat = sum(lat_r[m]["mean_ms"] for m in rag_mods) / len(rag_mods)
            rows.append(["Latence", "RAG (moy.)", f"{avg_rag_lat:.0f}ms"])

    table = ax6.table(cellText=rows[1:], colLabels=rows[0],
                      loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.6)
    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_facecolor("#2C3E50")
            cell.set_text_props(color="white", fontweight="bold")
        elif r % 2 == 0:
            cell.set_facecolor("#ECF0F1")
    ax6.set_title("Récapitulatif", fontsize=11, pad=12)

    path = out_dir / "summary_dashboard.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host",          default="http://localhost:8000")
    parser.add_argument("--skip-rag",      action="store_true")
    parser.add_argument("--skip-latency",  action="store_true")
    parser.add_argument("--latency-n",     type=int, default=2)
    args = parser.parse_args()

    base    = Path(__file__).parent
    out_dir = base / "results"
    out_dir.mkdir(exist_ok=True)

    # Ensure sub-modules are importable
    sys.path.insert(0, str(base.parent))

    intent_r = run_intent()

    rag_r = None
    if not args.skip_rag:
        try:
            rag_r = run_rag(args.host)
        except Exception as exc:
            print(f"  [WARNING] RAG eval failed: {exc}")

    lat_r = None
    if not args.skip_latency:
        try:
            lat_r = run_latency(args.host, args.latency_n)
        except Exception as exc:
            print(f"  [WARNING] Latency eval failed: {exc}")

    print("\n" + "="*60)
    print("  Génération du tableau de bord...")
    save_summary_dashboard(intent_r, rag_r, lat_r, out_dir)

    # Consolidated report
    report = {
        "generated_at": datetime.now().isoformat(),
        "intent":       intent_r,
        "rag":          rag_r,
        "latency":      lat_r,
    }
    report_path = out_dir / "evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    print(f"  Saved: {report_path}")

    print("\n" + "="*60)
    print("  ÉVALUATION COMPLÈTE")
    print(f"  Intent  — Accuracy: {intent_r['accuracy']:.1%}  Macro F1: {intent_r['macro_f1']:.1%}")
    if rag_r:
        print(f"  RAG     — Relevance: {rag_r['avg_relevance']:.1%}  Exact Match: {rag_r['exact_match_rate']:.1%}")
    if lat_r:
        net_mods = [m for m in lat_r if "offline" not in m.lower() and lat_r[m]["mean_ms"] > 1]
        if net_mods:
            avg_net = sum(lat_r[m]["mean_ms"] for m in net_mods) / len(net_mods)
            print(f"  Latence — Moyenne réseau: {avg_net:.0f}ms")
    print(f"  Résultats dans : {out_dir}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
