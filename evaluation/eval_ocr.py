"""
OCR Passport Evaluation
Tests the OCR endpoint against synthetic passport images with known ground truth.

Metrics:
  - Field Accuracy      : % of fields correctly extracted per passport
  - MRZ Parse Rate      : % of passports where MRZ was successfully parsed
  - Per-field Accuracy  : accuracy per field (surname, given_names, passport_number, etc.)
  - CER (Char Error Rate): character-level edit distance for text fields

Usage:
    python evaluation/eval_ocr.py [--host http://localhost:8000]
"""

import argparse
import json
from pathlib import Path

import httpx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize_field(val: str | None) -> str:
    if not val:
        return ""
    return val.upper().strip().replace("<", " ").replace("  ", " ").strip()


def cer(expected: str, predicted: str) -> float:
    """Character Error Rate via Levenshtein distance."""
    e, p = expected.upper(), predicted.upper()
    if not e:
        return 0.0 if not p else 1.0
    m, n = len(e), len(p)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[:]
        dp[0] = i
        for j in range(1, n + 1):
            cost = 0 if e[i-1] == p[j-1] else 1
            dp[j] = min(dp[j] + 1, dp[j-1] + 1, prev[j-1] + cost)
    return dp[n] / max(m, n)


FIELDS_TO_EVAL = [
    ("passport_number", "passport_number"),
    ("surname",         "surname"),
    ("given_names",     "given_names"),
    ("nationality",     "nationality"),
    ("sex",             "sex"),
]


def field_match(expected: str, predicted: str) -> bool:
    return normalize_field(expected) == normalize_field(predicted)


# ---------------------------------------------------------------------------
# OCR endpoint call
# ---------------------------------------------------------------------------

def call_ocr(host: str, image_path: Path) -> dict:
    url = f"{host}/api/ocr/passport"
    try:
        with open(image_path, "rb") as f:
            resp = httpx.post(
                url,
                files={"file": (image_path.name, f, "image/jpeg")},
                data={"client_id": f"eval_ocr_{image_path.stem}"},
                timeout=60,
            )
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        return {"error": str(exc), "passport_data": {}}


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

def save_per_field_chart(per_field: dict, out_dir: Path):
    fields = list(per_field.keys())
    accs   = [per_field[f]["accuracy"] for f in fields]
    colors = ["#4C72B0" if a >= 0.8 else "#C44E52" for a in accs]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(fields, accs, color=colors, edgecolor="white")
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Accuracy", fontsize=11)
    ax.set_title("OCR Passeport - Accuracy par Champ", fontsize=13)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    for bar, v in zip(bars, accs):
        ax.text(bar.get_x() + bar.get_width()/2, v + 0.02,
                f"{v:.0%}", ha="center", fontsize=10, fontweight="bold")
    plt.tight_layout()
    path = out_dir / "ocr_per_field.png"
    fig.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


def save_summary_chart(results: list, out_dir: Path):
    ids     = [f"#{r['id']}" for r in results]
    accs    = [r["field_accuracy"] for r in results]
    mrz_ok  = [1 if r["mrz_parsed"] else 0 for r in results]

    x = np.arange(len(ids))
    w = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - w/2, accs,   w, label="Field Accuracy", color="#4C72B0")
    ax.bar(x + w/2, mrz_ok, w, label="MRZ Parse",      color="#55A868", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(ids)
    ax.set_ylim(0, 1.2)
    ax.set_ylabel("Score", fontsize=11)
    ax.set_title("OCR Passeport - Resultats par Passeport Test", fontsize=13)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    path = out_dir / "ocr_per_passport.png"
    fig.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="http://localhost:8000")
    args = parser.parse_args()

    base      = Path(__file__).parent
    img_dir   = base / "results" / "passports"
    gt_path   = img_dir / "ground_truth.json"
    out_dir   = base / "results"
    out_dir.mkdir(exist_ok=True)

    with open(gt_path, encoding="utf-8") as f:
        ground_truth = json.load(f)
    gt_by_id = {g["id"]: g for g in ground_truth}

    print(f"\n{'='*55}")
    print("  Rihla-AI -- Evaluation OCR Passeport")
    print(f"  Backend : {args.host}")
    print(f"{'='*55}\n")

    records = []
    per_field_hits  = {f[0]: [] for f in FIELDS_TO_EVAL}

    for item in ground_truth:
        pid      = item["id"]
        img_path = img_dir / item["filename"]
        if not img_path.exists():
            print(f"  [SKIP] #{pid} — fichier introuvable: {img_path.name}")
            continue
        gt  = gt_by_id.get(pid, {})

        print(f"  Passeport #{pid} — {img_path.name}")
        result = call_ocr(args.host, img_path)

        if "error" in result and result["error"]:
            print(f"    [ERR] {result['error'][:80]}\n")
            records.append({"id": pid, "error": result["error"],
                            "field_accuracy": 0.0, "mrz_parsed": False})
            continue

        pp = result.get("passport_data", {})
        mrz_parsed = bool(pp.get("mrz_line1") or pp.get("passport_number"))

        # Evaluate fields
        field_results = {}
        hits = 0
        for gt_key, pred_key in FIELDS_TO_EVAL:
            expected  = normalize_field(gt.get(gt_key, ""))
            predicted = normalize_field(pp.get(pred_key, ""))
            match     = field_match(expected, predicted)
            char_err  = cer(expected, predicted)
            hits      += int(match)
            per_field_hits[gt_key].append(int(match))
            field_results[gt_key] = {
                "expected":  expected,
                "predicted": predicted,
                "match":     match,
                "cer":       round(char_err, 3),
            }
            status = "OK" if match else "XX"
            print(f"    [{status}] {gt_key:<20} expected={expected:<20} "
                  f"got={predicted[:20]:<20} CER={char_err:.2f}")

        field_acc = hits / len(FIELDS_TO_EVAL)
        mrz_tag   = "OK" if mrz_parsed else "XX"
        print(f"    MRZ parsed: [{mrz_tag}]  Field Accuracy: {field_acc:.0%}\n")

        records.append({
            "id":             pid,
            "field_accuracy": round(field_acc, 4),
            "mrz_parsed":     mrz_parsed,
            "fields":         field_results,
            "error":          None,
        })

    # Aggregates
    valid = [r for r in records if not r.get("error")]
    avg_field_acc = float(np.mean([r["field_accuracy"] for r in valid])) if valid else 0
    mrz_parse_rate = float(np.mean([r["mrz_parsed"] for r in valid]))    if valid else 0

    per_field_acc = {
        f: {"accuracy": round(float(np.mean(hits)), 4), "n": len(hits)}
        for f, hits in per_field_hits.items()
        if hits
    }
    avg_cer = float(np.mean([
        r["fields"][f]["cer"]
        for r in valid if r.get("fields")
        for f in per_field_hits
        if f in r["fields"]
    ])) if valid else 0

    print(f"{'-'*55}")
    print(f"  Field Accuracy moyenne  : {avg_field_acc:.1%}")
    print(f"  MRZ Parse Rate          : {mrz_parse_rate:.1%}")
    print(f"  CER moyen               : {avg_cer:.3f}")
    print(f"{'-'*55}")
    print(f"\n  Par champ:")
    for f, m in per_field_acc.items():
        print(f"    {f:<22} Accuracy={m['accuracy']:.0%}")

    print("\n  Generation des graphiques...")
    if per_field_acc:
        save_per_field_chart(per_field_acc, out_dir)
    if valid:
        save_summary_chart(valid, out_dir)

    results = {
        "avg_field_accuracy": round(avg_field_acc, 4),
        "mrz_parse_rate":     round(mrz_parse_rate, 4),
        "avg_cer":            round(avg_cer, 4),
        "n_total":            len(records),
        "n_success":          len(valid),
        "per_field":          per_field_acc,
        "records":            records,
    }
    json_path = out_dir / "ocr_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {json_path}")
    print(f"\n{'='*55}\n")

    return results


if __name__ == "__main__":
    main()
