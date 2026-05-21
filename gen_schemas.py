"""
Generate 3 schemas for Rihla-AI report.

Key design choices:
  - bbox_inches=None  → exact figsize × DPI pixels (no auto-cropping)
  - subplots_adjust   → axes fills 96% of figure
  - Font sizes tuned to fit inside their respective box widths
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

WHITE = 'white'
DARK  = '#1A237E'
GRAY  = '#546E7A'


def _setup(figw, figh):
    fig, ax = plt.subplots(figsize=(figw, figh))
    plt.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor(WHITE)
    return fig, ax


def _box(ax, cx, cy, w, h, title, sub=None,
         ec='#1565C0', fc='#E3F2FD', tfs=28, sfs=20):
    ax.add_patch(mpatches.FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.5",
        facecolor=fc, edgecolor=ec, linewidth=2.5, zorder=3))
    if sub:
        ax.text(cx, cy + 2.2, title, fontsize=tfs, fontweight='bold',
                ha='center', va='center', color=DARK, zorder=4,
                multialignment='center')
        ax.text(cx, cy - 3.0, sub, fontsize=sfs,
                ha='center', va='center', color=GRAY, zorder=4,
                multialignment='center')
    else:
        ax.text(cx, cy, title, fontsize=tfs, fontweight='bold',
                ha='center', va='center', color=DARK, zorder=4,
                multialignment='center')


def _bg(ax, x, y, w, h, ec, fc, alpha=0.45):
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.5",
        facecolor=fc, edgecolor=ec, linewidth=2.0, alpha=alpha, zorder=1))


def _harrow(ax, x1, x2, y, color, lw=2.5):
    ax.annotate('', xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw), zorder=5)


def _varrow(ax, x, y1, y2, color, lw=2.5):
    ax.annotate('', xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw), zorder=5)


# ─────────────────────────────────────────────────────────────────────────────
# 1. RAG PIPELINE  —  figsize=(12,9)  →  2400×1800 px  (bbox_inches=None)
# At 1920-px screen width: scale=0.8  →  30pt≈67px, 21pt≈47px  (readable)
# ─────────────────────────────────────────────────────────────────────────────

def gen_rag():
    BLUE    = '#1565C0';  BLUE_BG  = '#E3F2FD'
    GREEN   = '#2E7D32';  GREEN_BG = '#E8F5E9'

    fig, ax = _setup(12, 9)

    # Titles  (y=95 gives enough room above Phase-1 band at y=87)
    ax.text(50, 95.5, "Pipeline RAG",
            fontsize=42, fontweight='bold', ha='center', va='center', color=DARK)
    ax.text(50, 89.5, "Retrieval-Augmented Generation",
            fontsize=27, style='italic', ha='center', va='center', color=GRAY)

    # ── Phase 1  y: 46 → 87 ──────────────────────────────────────────────────
    _bg(ax, 1.5, 46, 97, 41, BLUE, '#EBF5FB')
    ax.text(50, 84, "Phase 1  —  Indexation des Donnees",
            fontsize=27, fontweight='bold', ha='center', va='center', color=BLUE, zorder=2)

    # 4 boxes: w=22, gap=3, margins=1.5  →  centres 12.5, 37.5, 62.5, 87.5
    p1 = [(12.5, "Documents",  "Agence"),
          (37.5, "Chunking",   "Decoupage\ntexte"),
          (62.5, "Embedding",  "nomic-\nembed-text"),
          (87.5, "Qdrant",     "rihla_fr\nrihla_ar")]
    for cx, t, s in p1:
        _box(ax, cx, 63, 22, 16, t, s, BLUE, BLUE_BG, tfs=28, sfs=20)

    for xs in [23.5, 48.5, 73.5]:       # right-edge → left-edge of next
        _harrow(ax, xs, xs + 3, 63, BLUE)

    # ── Phase 2  y: 4 → 43 ───────────────────────────────────────────────────
    _bg(ax, 1.5, 4, 97, 39, GREEN, '#E8F5E9')
    ax.text(50, 40, "Phase 2  —  Generation de Reponse",
            fontsize=27, fontweight='bold', ha='center', va='center', color=GREEN, zorder=2)

    # 5 boxes: w=17, gap=2.5, margins=2.5  →  centres 11, 30.5, 50, 69.5, 89
    p2 = [(11,   "Question",  "Client"),
          (30.5, "Embedding", "768 dim."),
          (50,   "Recherche", "Top-K\ncosinus"),
          (69.5, "LLM",       "Qwen 2.5\n7B"),
          (89,   "Reponse",   "Factuelle")]
    for cx, t, s in p2:
        _box(ax, cx, 23, 17, 16, t, s, GREEN, GREEN_BG, tfs=25, sfs=19)

    for xs in [19.5, 39, 58.5, 78]:
        _harrow(ax, xs, xs + 2.5, 23, GREEN)

    # Qdrant → Recherche cross-phase arc
    ax.annotate('', xy=(50, 31), xytext=(87.5, 55),
                arrowprops=dict(arrowstyle='->', color='#90A4AE', lw=2.0,
                                connectionstyle='arc3,rad=-0.22',
                                linestyle='dashed'), zorder=5)
    ax.text(80, 48, "Top-K\nvecteurs", fontsize=18,
            ha='center', va='center', color='#78909C', style='italic')

    plt.savefig('schema_rag_pipeline.png', dpi=200,
                facecolor=WHITE, bbox_inches=None)
    plt.close()
    print("Done: schema_rag_pipeline.png")


# ─────────────────────────────────────────────────────────────────────────────
# 2. OCR PIPELINE  —  figsize=(12,10)  →  2400×2000 px
# ─────────────────────────────────────────────────────────────────────────────

def gen_ocr():
    ORANGE  = '#E65100';  ORANGE_BG = '#FFF3E0'
    PURPLE  = '#4A148C';  PURPLE_BG = '#F3E5F5'
    TEAL    = '#00695C';  TEAL_BG   = '#E0F2F1'

    fig, ax = _setup(12, 10)

    ax.text(50, 96, "Pipeline OCR",
            fontsize=42, fontweight='bold', ha='center', va='center', color=DARK)
    ax.text(50, 91, "Extraction automatique  —  Passeport",
            fontsize=27, style='italic', ha='center', va='center', color=GRAY)

    # Input
    _box(ax, 50, 83, 46, 11, "Image Passeport",
         "Document d'identite numerise",
         ec='#455A64', fc='#ECEFF1', tfs=30, sfs=22)

    # T-junction splitter
    _varrow(ax, 50, 77.5, 73, '#455A64')
    ax.plot([24, 76], [73, 73], color='#455A64', lw=2.5, zorder=4)
    _varrow(ax, 24, 73, 68.5, ORANGE)
    _varrow(ax, 76, 73, 68.5, PURPLE)

    # LEFT path background
    _bg(ax, 4, 31, 40, 42, ORANGE, ORANGE_BG, alpha=0.30)
    ax.text(24, 73.5, "Moteur principal", fontsize=22, fontweight='bold',
            ha='center', va='bottom', color=ORANGE, zorder=4)

    _box(ax, 24, 60, 36, 14, "EasyOCR",
         "PyTorch  |  CPU Docker",
         ec=ORANGE, fc=ORANGE_BG, tfs=30, sfs=22)

    _varrow(ax, 24, 53, 48, ORANGE)

    _box(ax, 24, 41, 36, 12, "pytesseract",
         "Fallback leger",
         ec='#BF360C', fc='#FBE9E7', tfs=28, sfs=22)

    # RIGHT path background
    _bg(ax, 56, 31, 40, 42, PURPLE, PURPLE_BG, alpha=0.30)
    ax.text(76, 73.5, "MRZ ISO 9303", fontsize=22, fontweight='bold',
            ha='center', va='bottom', color=PURPLE, zorder=4)

    _box(ax, 76, 60, 36, 14, "passporteye",
         "Detection MRZ",
         ec=PURPLE, fc=PURPLE_BG, tfs=30, sfs=22)

    _varrow(ax, 76, 53, 48, PURPLE)

    _box(ax, 76, 41, 36, 12, "Lignes MRZ",
         "Ligne 1  +  Ligne 2",
         ec='#6A1B9A', fc='#EDE7F6', tfs=28, sfs=22)

    # Merge both paths
    ax.annotate('', xy=(50, 29), xytext=(24, 35),
                arrowprops=dict(arrowstyle='->', color='#455A64', lw=2.5,
                                connectionstyle='angle,angleA=-90,angleB=180'), zorder=5)
    ax.annotate('', xy=(50, 29), xytext=(76, 35),
                arrowprops=dict(arrowstyle='->', color='#455A64', lw=2.5,
                                connectionstyle='angle,angleA=-90,angleB=0'), zorder=5)
    _varrow(ax, 50, 29, 24, TEAL)

    # Output box  (wide, w=88 fits on 100-unit axis with margin 6 each side)
    _box(ax, 50, 15, 88, 16, "Donnees Structurees",
         "Nom   |   Prenom   |   N Passeport   |   Date Naissance   |   Expiration   |   Nationalite",
         ec=TEAL, fc=TEAL_BG, tfs=30, sfs=18)

    plt.savefig('schema_ocr_pipeline.png', dpi=200,
                facecolor=WHITE, bbox_inches=None)
    plt.close()
    print("Done: schema_ocr_pipeline.png")


# ─────────────────────────────────────────────────────────────────────────────
# 3. ARCHITECTURE  —  figsize=(13,12)  →  2600×2400 px
#
# y layout (bottom → top, total = 100 units):
#   2  | Couche 5  bg  h=19  [2,21]
#   3  | arrow gap        [21,24]
#   22 | Couche 4  bg  h=22  [24,46]
#   3  | arrow gap        [46,49]
#   12 | Couche 3  bg  h=12  [49,61]
#   3  | arrow gap        [61,64]
#   12 | Couche 2  bg  h=12  [64,76]
#   3  | arrow gap        [76,79]
#   13 | Couche 1  bg  h=13  [79,92]
#   8  | title/subtitle       [92,100]
# ─────────────────────────────────────────────────────────────────────────────

def gen_arch():
    SLATE   = '#455A64';  SLATE_BG  = '#ECEFF1'
    BLUE    = '#1565C0';  BLUE_BG   = '#E3F2FD'
    GREEN   = '#2E7D32';  GREEN_BG  = '#E8F5E9'
    ORANGE  = '#E65100';  ORANGE_BG = '#FFF3E0'
    TEAL    = '#004D40';  TEAL_BG   = '#E0F2F1'

    fig, ax = _setup(13, 12)

    ax.text(50, 97, "Architecture Rihla-AI",
            fontsize=42, fontweight='bold', ha='center', va='center', color=DARK)
    ax.text(50, 93, "Vue d'ensemble  —  5 couches fonctionnelles",
            fontsize=27, style='italic', ha='center', va='center', color=GRAY)

    LBL = 22   # band label fontsize (used for all 5 couches)
    BFS = 28   # sub-box title
    BSB = 20   # sub-box subtitle
    WFS = 20   # wide-box content

    # ── Couche 1: Canaux d'entree  (bg y=[79, 92]) ───────────────────────────
    _bg(ax, 3, 79, 94, 13, SLATE, SLATE_BG, alpha=0.4)
    ax.text(50, 91, "Couche 1  —  Canaux d'entree",
            fontsize=LBL, fontweight='bold', ha='center', va='center',
            color=SLATE, zorder=2)

    _box(ax, 28, 84, 44, 9, "WhatsApp", "via WAHA API",
         ec='#1B5E20', fc='#C8E6C9', tfs=BFS, sfs=BSB)
    _box(ax, 72, 84, 44, 9, "Email", "IMAP / SMTP",
         ec='#B71C1C', fc='#FFCDD2', tfs=BFS, sfs=BSB)

    _varrow(ax, 50, 79, 76, SLATE)

    # ── Couche 2: Orchestration n8n  (bg y=[64, 76]) ─────────────────────────
    _bg(ax, 3, 64, 94, 12, BLUE, BLUE_BG, alpha=0.45)
    ax.text(50, 74.5, "Couche 2  —  Orchestration  n8n",
            fontsize=LBL, fontweight='bold', ha='center', va='center',
            color=BLUE, zorder=2)
    _box(ax, 50, 68, 88, 8,
         "Workflows  |  Routage des intents  |  Webhooks",
         sub=None, ec=BLUE, fc=BLUE_BG, tfs=WFS, sfs=0)

    _varrow(ax, 50, 64, 61, BLUE)

    # ── Couche 3: Backend FastAPI  (bg y=[49, 61]) ────────────────────────────
    _bg(ax, 3, 49, 94, 12, GREEN, GREEN_BG, alpha=0.45)
    ax.text(50, 59.5, "Couche 3  —  Backend  FastAPI",
            fontsize=LBL, fontweight='bold', ha='center', va='center',
            color=GREEN, zorder=2)
    _box(ax, 50, 53, 88, 8,
         "Python 3.12  |  /conversations  |  /ocr  |  /recommend",
         sub=None, ec=GREEN, fc=GREEN_BG, tfs=WFS, sfs=0)

    _varrow(ax, 50, 49, 46, GREEN)

    # ── Couche 4: Intelligence  (bg y=[24, 46]) ───────────────────────────────
    _bg(ax, 3, 24, 94, 22, ORANGE, ORANGE_BG, alpha=0.35)
    ax.text(50, 44.5, "Couche 4  —  Intelligence artificielle",
            fontsize=LBL, fontweight='bold', ha='center', va='center',
            color=ORANGE, zorder=2)

    for cx, t, s in [(17.5, "LLM + RAG",    "Qwen 2.5 7B\n+ Qdrant"),
                     (50,   "OCR",           "EasyOCR\n+ passporteye"),
                     (82.5, "Recommandeur",  "LightGBM\n22 features")]:
        _box(ax, cx, 33, 27, 16, t, s, ORANGE, ORANGE_BG, tfs=BFS, sfs=BSB)

    _varrow(ax, 50, 24, 21, TEAL)

    # ── Couche 5: Stockage  (bg y=[2, 21]) ───────────────────────────────────
    _bg(ax, 3, 2, 94, 19, TEAL, TEAL_BG, alpha=0.35)
    ax.text(50, 20, "Couche 5  —  Stockage des donnees",
            fontsize=LBL, fontweight='bold', ha='center', va='center',
            color=TEAL, zorder=2)

    for cx, t, s in [(17.5, "PostgreSQL",  "12 tables\n11 programmes"),
                     (50,   "Redis",        "Contexte conv.\nTTL 24h"),
                     (82.5, "Qdrant",       "768-dim vectors\nrihla_fr / rihla_ar")]:
        _box(ax, cx, 9.5, 27, 14, t, s, TEAL, TEAL_BG, tfs=BFS, sfs=BSB)

    plt.savefig('schema_architecture_haut_niveau.png', dpi=200,
                facecolor=WHITE, bbox_inches=None)
    plt.close()
    print("Done: schema_architecture_haut_niveau.png")


if __name__ == '__main__':
    gen_rag()
    gen_ocr()
    gen_arch()
    print("\nAll 3 schemas generated.")
