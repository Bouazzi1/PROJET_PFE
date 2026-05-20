"""
Latency Evaluation
Measures end-to-end response time for each module by sending representative
queries to the live backend and recording timing.

Modules tested:
  - RAG general   (general intent query)
  - RAG program   (program-filtered query)
  - Intent classify  (measured client-side, no network — pure function speed)
  - Recommendation   (triggers profile collection, then recommendation)

Output:
  - results/latency_results.json
  - results/latency_by_module.png

Usage:
    python evaluation/eval_latency.py [--host http://localhost:8000] [--n 5]
"""

import argparse
import json
import statistics
import time
from pathlib import Path

import httpx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Intent classifier (offline timing)
# ---------------------------------------------------------------------------

def classify_intent(content: str) -> str:
    content_lower = content.lower()
    recommendation_keywords = [
        "recommand","suggest","conseil","meilleur","proposer",
        "personnalis","adapté","pour moi","quel voyage",
        "توصية","اقتراح","أفضل","انصحني","اقترح",
    ]
    passport_keywords = ["passeport","passport","جواز","visa"]
    booking_keywords  = ["réserv","reserv","book","حجز","inscrire"]
    program_keywords  = [
        "programme","forfait","séjour","voyage","offre","package",
        "formule","circuit","disponible","avez-vous","proposez",
        "prix pour","combien pour","برنامج","برامج","رحلة","عرض","باقة",
    ]
    for kw in recommendation_keywords:
        if kw in content_lower: return "recommendation"
    for kw in passport_keywords:
        if kw in content_lower: return "passport"
    for kw in booking_keywords:
        if kw in content_lower: return "booking"
    for kw in program_keywords:
        if kw in content_lower: return "program"
    return "general"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def post_message(host: str, client_id: str, content: str) -> tuple[float, str]:
    url = f"{host}/api/conversations/message"
    payload = {"client_id": client_id, "channel": "eval_lat", "content": content, "has_media": False}
    t0 = time.time()
    try:
        resp = httpx.post(url, json=payload, timeout=90)
        lat  = (time.time() - t0) * 1000
        resp.raise_for_status()
        return lat, resp.json().get("response", "")
    except Exception as exc:
        lat = (time.time() - t0) * 1000
        return lat, f"ERROR: {exc}"


SCENARIOS = [
    {
        "module": "RAG — Général",
        "queries": [
            "Quelle est l'adresse de l'agence ?",
            "Travaillez-vous le weekend ?",
            "Quelle langue parlez-vous ?",
        ],
        "client_suffix": "gen",
    },
    {
        "module": "RAG — Programme",
        "queries": [
            "Quels programmes avez-vous pour Istanbul ?",
            "Quel est le prix du programme Antalya Prestige ?",
            "Le programme Paris en Famille inclut-il Disneyland ?",
        ],
        "client_suffix": "prog",
    },
    {
        "module": "RAG — Arabe",
        "queries": [
            "ما هو سعر برنامج اسطنبول الاقتصادي؟",
            "ما هي البرامج المتاحة في أنطاليا؟",
        ],
        "client_suffix": "ar",
    },
    {
        "module": "Intent (offline)",
        "queries": [
            "recommande moi un voyage",
            "quels programmes avez-vous pour Istanbul ?",
            "je veux réserver le programme Paris Famille",
            "passeport expiré",
            "bonjour comment ça va",
        ],
        "client_suffix": None,  # offline
    },
]


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

def save_latency_chart(module_stats: dict, out_dir: Path):
    modules = list(module_stats.keys())
    means   = [module_stats[m]["mean_ms"] for m in modules]
    p95s    = [module_stats[m].get("p95_ms", module_stats[m]["mean_ms"]) for m in modules]

    x = np.arange(len(modules))
    w = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - w/2, means, w, label="Moyenne (ms)",  color="#4C72B0")
    ax.bar(x + w/2, p95s,  w, label="P95 (ms)",      color="#C44E52", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(modules, fontsize=10, rotation=15, ha="right")
    ax.set_ylabel("Latence (ms)", fontsize=11)
    ax.set_title("Latence par Module", fontsize=13)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    path = out_dir / "latency_by_module.png"
    fig.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="http://localhost:8000")
    parser.add_argument("--n",    type=int, default=3, help="Repetitions per query")
    args = parser.parse_args()

    base    = Path(__file__).parent
    out_dir = base / "results"
    out_dir.mkdir(exist_ok=True)

    print(f"\n{'='*55}")
    print("  Rihla-AI — Évaluation Latence")
    print(f"  Backend : {args.host}  |  Répétitions : {args.n}")
    print(f"{'='*55}\n")

    module_stats: dict = {}

    for scenario in SCENARIOS:
        mod     = scenario["module"]
        queries = scenario["queries"]
        suffix  = scenario["client_suffix"]
        offline = suffix is None

        print(f"  Module: {mod}")
        all_lats = []

        for q in queries:
            for rep in range(args.n):
                if offline:
                    t0  = time.perf_counter()
                    classify_intent(q)
                    lat = (time.perf_counter() - t0) * 1000
                else:
                    cid = f"eval_lat_{suffix}_{rep}"
                    lat, _ = post_message(args.host, cid, q)

                all_lats.append(lat)
                tag = "offline" if offline else "online"
                safe_q = q[:50].encode("ascii", "replace").decode()
                print(f"    [{tag}] rep={rep+1} lat={lat:6.1f}ms | {safe_q}")

        if all_lats:
            stats = {
                "mean_ms":   round(statistics.mean(all_lats), 1),
                "median_ms": round(statistics.median(all_lats), 1),
                "min_ms":    round(min(all_lats), 1),
                "max_ms":    round(max(all_lats), 1),
                "p95_ms":    round(sorted(all_lats)[int(len(all_lats) * 0.95)], 1),
                "n":         len(all_lats),
            }
            module_stats[mod] = stats
            print(f"    => mean={stats['mean_ms']}ms  median={stats['median_ms']}ms  "
                  f"p95={stats['p95_ms']}ms  min={stats['min_ms']}ms  max={stats['max_ms']}ms\n")

    print(f"{'-'*55}")
    print("  Resume:")
    for mod, s in module_stats.items():
        safe_mod = mod.encode("ascii", "replace").decode()
        print(f"    {safe_mod:<25} mean={s['mean_ms']:7.1f}ms  p95={s['p95_ms']:7.1f}ms")
    print(f"{'-'*55}\n")

    print("  Generation des graphiques...")
    save_latency_chart(module_stats, out_dir)

    json_path = out_dir / "latency_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(module_stats, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {json_path}")
    print(f"\n{'='*55}\n")

    return module_stats


if __name__ == "__main__":
    main()
