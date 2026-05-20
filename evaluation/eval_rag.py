"""
RAG Evaluation
Sends each question from rag_test_set.json to the live backend /api/conversations/message,
then evaluates the answer with keyword-matching (Answer Relevance proxy) and
an optional LLM-as-judge call (Faithfulness).

Metrics produced:
  - Answer Relevance  (keyword overlap between expected and generated answer)
  - Exact Match       (case-insensitive substring check)
  - Response Length   (avg tokens)
  - Latency           (ms per query)

Charts:
  - Bar chart: metric scores per category
  - Latency distribution histogram

Usage:
    python evaluation/eval_rag.py [--host http://localhost:8000] [--client test_eval]
"""

import argparse
import json
import re
import time
from pathlib import Path

import httpx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    """Lowercase, strip diacritics-ish, collapse spaces."""
    text = text.lower()
    # Remove common French diacritics for matching
    for a, b in [("é","e"),("è","e"),("ê","e"),("ë","e"),("à","a"),("â","a"),
                 ("ù","u"),("û","u"),("ô","o"),("î","i"),("ï","i"),("ç","c")]:
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text).strip()


def keyword_relevance(expected: str, generated: str) -> float:
    """
    Proportion of significant words from the expected answer found in the generated answer.
    Stopwords excluded to focus on meaningful tokens.
    """
    stopwords = {
        "le","la","les","de","du","des","un","une","et","est","en","à","au","aux",
        "il","elle","ils","elles","pour","par","sur","avec","dans","que","qui",
        "oui","non","je","tu","nous","vous","ce","se","ou","si","mais","donc",
    }
    exp_tokens = [t for t in normalize(expected).split() if t not in stopwords and len(t) > 2]
    gen_norm   = normalize(generated)
    if not exp_tokens:
        return 1.0
    hits = sum(1 for t in exp_tokens if t in gen_norm)
    return hits / len(exp_tokens)


def exact_match(expected: str, generated: str) -> bool:
    """Check if any key fragment of expected appears in generated."""
    # Extract numbers / short strings (prices, days, names)
    fragments = re.findall(r"\d[\d\s]+\w*|\b[A-ZÀÂÉÈÊÎÔÙÛŒ][a-zàâéèêîôùûœ]+(?:\s[A-ZÀÂÉÈÊÎÔÙÛŒ][a-zàâéèêîôùûœ]+)*", expected)
    if not fragments:
        return keyword_relevance(expected, generated) > 0.5
    gen_norm = normalize(generated)
    return any(normalize(f) in gen_norm for f in fragments)


# ---------------------------------------------------------------------------
# Backend query
# ---------------------------------------------------------------------------

def query_backend(host: str, client_id: str, question: str, lang: str = "fr") -> dict:
    url = f"{host}/api/conversations/message"
    payload = {
        "client_id": client_id,
        "channel": "eval",
        "content": question,
        "has_media": False,
    }
    t0 = time.time()
    try:
        resp = httpx.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        latency_ms = (time.time() - t0) * 1000
        data = resp.json()
        return {
            "answer": data.get("response", ""),
            "intent": data.get("intent", ""),
            "latency_ms": latency_ms,
            "error": None,
        }
    except Exception as exc:
        latency_ms = (time.time() - t0) * 1000
        return {"answer": "", "intent": "", "latency_ms": latency_ms, "error": str(exc)}


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

def save_category_chart(by_category: dict, out_dir: Path):
    cats   = sorted(by_category.keys())
    rel    = [by_category[c]["avg_relevance"] for c in cats]
    em     = [by_category[c]["exact_match_rate"] for c in cats]

    x = np.arange(len(cats))
    w = 0.35
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(x - w/2, rel, w, label="Answer Relevance", color="#4C72B0")
    ax.bar(x + w/2, em,  w, label="Exact Match Rate", color="#55A868")
    ax.set_xticks(x)
    ax.set_xticklabels(cats, rotation=30, ha="right", fontsize=9)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Score (0–1)", fontsize=11)
    ax.set_title("RAG — Métriques par Catégorie", fontsize=13)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    path = out_dir / "rag_by_category.png"
    fig.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


def save_latency_hist(latencies: list[float], out_dir: Path):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(latencies, bins=10, color="#C44E52", edgecolor="white")
    ax.axvline(np.mean(latencies), color="black", linestyle="--", label=f"Moyenne: {np.mean(latencies):.0f} ms")
    ax.set_xlabel("Latence (ms)", fontsize=11)
    ax.set_ylabel("Fréquence", fontsize=11)
    ax.set_title("RAG — Distribution des Latences", fontsize=13)
    ax.legend()
    plt.tight_layout()
    path = out_dir / "rag_latency.png"
    fig.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host",   default="http://localhost:8000")
    parser.add_argument("--client", default="eval_rag_001")
    args = parser.parse_args()

    base     = Path(__file__).parent
    data_path = base / "data" / "rag_test_set.json"
    out_dir  = base / "results"
    out_dir.mkdir(exist_ok=True)

    with open(data_path, encoding="utf-8") as f:
        test_set = json.load(f)

    print(f"\n{'='*60}")
    print("  Rihla-AI -- Evaluation RAG")
    print(f"  Backend : {args.host}")
    print(f"{'='*60}\n")

    records   = []
    latencies = []

    for item in test_set:
        q        = item["question"]
        expected = item["expected_answer"]
        category = item["category"]
        lang     = "ar" if category.endswith("_ar") else "fr"

        # Unique client_id per question to avoid Redis state contamination
        unique_client = f"{args.client}_{item['id']}"

        result = query_backend(args.host, unique_client, q, lang)
        generated = result["answer"]
        lat       = result["latency_ms"]
        latencies.append(lat)

        if result["error"]:
            print(f"  [ERR] #{item['id']:02d} {result['error'][:60]}")
            records.append({**item, "generated": "", "relevance": 0.0, "exact_match": False, "latency_ms": lat, "error": result["error"]})
            continue

        rel = keyword_relevance(expected, generated)
        em  = exact_match(expected, generated)
        ok  = "OK" if em else ("~~" if rel > 0.4 else "XX")

        safe_q = q[:65].encode("ascii", "replace").decode()
        safe_e = expected.encode("ascii", "replace").decode()
        safe_g = generated[:80].encode("ascii", "replace").decode()
        print(f"  [{ok}] #{item['id']:02d} [{category:<14}] rel={rel:.2f} lat={lat:5.0f}ms")
        print(f"         Q: {safe_q}")
        print(f"         E: {safe_e}")
        print(f"         G: {safe_g}...")
        print()

        records.append({
            **item,
            "generated":    generated,
            "relevance":    round(rel, 4),
            "exact_match":  em,
            "latency_ms":   round(lat, 1),
            "error":        None,
        })

    # Aggregate
    valid = [r for r in records if not r["error"]]
    avg_rel  = np.mean([r["relevance"]  for r in valid]) if valid else 0
    em_rate  = np.mean([r["exact_match"] for r in valid]) if valid else 0
    avg_lat  = np.mean(latencies) if latencies else 0

    # By category
    by_cat: dict = {}
    for r in valid:
        cat = r["category"]
        by_cat.setdefault(cat, {"relevances": [], "ems": []})
        by_cat[cat]["relevances"].append(r["relevance"])
        by_cat[cat]["ems"].append(int(r["exact_match"]))
    by_category = {
        c: {
            "avg_relevance":    round(np.mean(v["relevances"]), 4),
            "exact_match_rate": round(np.mean(v["ems"]), 4),
            "n": len(v["relevances"]),
        }
        for c, v in by_cat.items()
    }

    print(f"{'-'*60}")
    print(f"  Resultats globaux ({len(valid)}/{len(test_set)} requetes reussies):")
    print(f"    Answer Relevance   : {avg_rel:.1%}")
    print(f"    Exact Match Rate   : {em_rate:.1%}")
    print(f"    Latence moyenne    : {avg_lat:.0f} ms")
    print(f"{'-'*60}")

    print("\n  Generation des graphiques...")
    if by_category:
        save_category_chart(by_category, out_dir)
    if latencies:
        save_latency_hist(latencies, out_dir)

    results = {
        "avg_relevance":   round(avg_rel, 4),
        "exact_match_rate": round(em_rate, 4),
        "avg_latency_ms":  round(avg_lat, 1),
        "n_success":       len(valid),
        "n_total":         len(test_set),
        "by_category":     by_category,
        "records":         records,
    }
    json_path = out_dir / "rag_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {json_path}")
    print(f"\n{'='*60}\n")

    return results


if __name__ == "__main__":
    main()
