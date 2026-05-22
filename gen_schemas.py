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
         ec='#1565C0', fc='#E3F2FD', tfs=28, sfs=20, tdy=2.2, sdy=-3.0):
    ax.add_patch(mpatches.FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.5",
        facecolor=fc, edgecolor=ec, linewidth=2.5, zorder=3))
    if sub:
        ax.text(cx, cy + tdy, title, fontsize=tfs, fontweight='bold',
                ha='center', va='center', color=DARK, zorder=4,
                multialignment='center')
        ax.text(cx, cy + sdy, sub, fontsize=sfs,
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


# ─────────────────────────────────────────────────────────────────────────────
# 4. WORKFLOW CONVERSATIONNEL  —  figsize=(12,12)  →  2400×2400 px
# Vertical layout: WhatsApp + Email (parallel) → n8n → FastAPI → Intent → 3 modules
# ─────────────────────────────────────────────────────────────────────────────

def gen_workflow():
    GREEN  = '#2E7D32';  GREEN_BG  = '#E8F5E9'
    BLUE   = '#1565C0';  BLUE_BG   = '#E3F2FD'
    ORANGE = '#E65100';  ORANGE_BG = '#FFF3E0'
    PURPLE = '#4A148C';  PURPLE_BG = '#F3E5F5'
    TEAL   = '#004D40';  TEAL_BG   = '#E0F2F1'
    RED    = '#B71C1C';  RED_BG    = '#FFCDD2'

    fig, ax = _setup(12, 12)

    ax.text(50, 97.5, "Workflow de traitement d'un message Rihla-AI",
            fontsize=30, fontweight='bold', ha='center', va='center', color=DARK)
    ax.text(50, 93, "Du canal d'entree a la reponse : classification d'intentions et routage",
            fontsize=22, style='italic', ha='center', va='center', color=GRAY)

    # ── Row 1: TWO PARALLEL input channels (y=82) ────────────────────────────
    _box(ax, 26, 82, 30, 12, "WhatsApp", "via WAHA API\nWebhook n8n",
         ec='#1B5E20', fc='#C8E6C9', tfs=26, sfs=18)
    _box(ax, 74, 82, 30, 12, "Email", "IMAP Reception\nWebhook n8n",
         ec=RED, fc=RED_BG, tfs=26, sfs=18)

    # Both channels converge independently to n8n
    ax.annotate('', xy=(42, 69), xytext=(26, 76),
                arrowprops=dict(arrowstyle='->', color='#455A64', lw=2.5,
                                connectionstyle='arc3,rad=0'), zorder=5)
    ax.annotate('', xy=(58, 69), xytext=(74, 76),
                arrowprops=dict(arrowstyle='->', color='#455A64', lw=2.5,
                                connectionstyle='arc3,rad=0'), zorder=5)

    # ── Row 2: n8n (y=63) ────────────────────────────────────────────────────
    _box(ax, 50, 63, 40, 12, "n8n", "Orchestration\nRoutage webhook",
         ec=BLUE, fc=BLUE_BG, tfs=26, sfs=18)
    _varrow(ax, 50, 57, 52, BLUE)

    # ── Row 3: FastAPI (y=45) ─────────────────────────────────────────────────
    _box(ax, 50, 45, 64, 12, "FastAPI",
         "Python 3.12  |  /conversations  |  /ocr  |  /recommend",
         ec=GREEN, fc=GREEN_BG, tfs=24, sfs=18)
    _varrow(ax, 50, 39, 34.5, GREEN)

    # ── Row 4: Intent Classifier (y=27) ──────────────────────────────────────
    _box(ax, 50, 27, 66, 13, "Classificateur d'intentions",
         "Analyse mots-cles  |  5 classes",
         ec=ORANGE, fc=ORANGE_BG, tfs=26, sfs=18)

    # ── Row 5: 3 output modules (cy=10, h=14 → spans 3 to 17) ───────────────
    modules = [
        (16, "RAG",          "Qwen 2.5 7B + Qdrant\ngeneral / programme", BLUE,   BLUE_BG),
        (50, "OCR",          "EasyOCR + passporteye\nextraction passeport", PURPLE, PURPLE_BG),
        (84, "Recommandeur", "LightGBM 22 features\nTop-3 programmes",    TEAL,   TEAL_BG),
    ]
    for cx, t, s, ec, fc in modules:
        _box(ax, cx, 10, 28, 14, t, s, ec=ec, fc=fc, tfs=25, sfs=18)
        ax.annotate('', xy=(cx, 17), xytext=(50, 20.5),
                    arrowprops=dict(arrowstyle='->', color=ORANGE, lw=2.2,
                                    connectionstyle='arc3,rad=0.0'), zorder=5)

    plt.savefig('schema_workflow_conversationnel.png', dpi=200,
                facecolor=WHITE, bbox_inches=None)
    plt.close()
    print("Done: schema_workflow_conversationnel.png")


# ─────────────────────────────────────────────────────────────────────────────
# 5. INTENT CLASSIFIER  —  figsize=(15,9)  →  3000×1800 px
# text → normalize → 5 keyword dicts → intent → routing
# ─────────────────────────────────────────────────────────────────────────────

def gen_intent():
    ORANGE = '#E65100';  ORANGE_BG = '#FFF3E0'
    BLUE   = '#1565C0';  BLUE_BG   = '#E3F2FD'
    GREEN  = '#2E7D32';  GREEN_BG  = '#E8F5E9'
    PURPLE = '#4A148C';  PURPLE_BG = '#F3E5F5'
    TEAL   = '#004D40';  TEAL_BG   = '#E0F2F1'

    fig, ax = _setup(15, 9)

    ax.text(50, 96.5, "Classificateur d'intentions Rihla-AI",
            fontsize=36, fontweight='bold', ha='center', va='center', color=DARK)
    ax.text(50, 92, "Normalisation → Detection par mots-cles → Routage vers le module cible",
            fontsize=22, style='italic', ha='center', va='center', color=GRAY)

    # ── Top pipeline: Message → Normalisation → Detection (y=76) ─────────────
    _box(ax, 7, 76, 12, 11, "Message\nclient", None,
         ec='#546E7A', fc='#ECEFF1', tfs=20)
    _box(ax, 27, 76, 22, 11, "Normalisation",
         "minuscules, sans accents",
         ec='#455A64', fc='#CFD8DC', tfs=20, sfs=16)
    # Detection: 1-line title + 1-line sub to prevent overlap
    _box(ax, 62, 76, 30, 11, "Detection mots-cles",
         "5 dictionnaires par classe",
         ec=ORANGE, fc=ORANGE_BG, tfs=20, sfs=16)

    _harrow(ax, 13, 16, 76, '#546E7A')
    _harrow(ax, 38, 47, 76, '#455A64')

    # Fallback note
    ax.text(62, 62, "Fallback : intention = general\nsi aucun mot-cle detecte",
            fontsize=13, style='italic', ha='center', va='center', color=GRAY,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF9C4',
                      edgecolor='#F9A825', linewidth=1.2), zorder=4)

    # ── 5 intent classes (cy=41, h=17, w=17) — spaced to avoid clipping ──────
    # cx: 10, 27.5, 50, 72.5, 90  (right edge: 98.5)
    intents = [
        (10,   "general",        BLUE,   BLUE_BG,   "bonjour, aide,\ninformation"),
        (27.5, "programme",      GREEN,  GREEN_BG,  "programme, voyage,\ndestination"),
        (50,   "reservation",    ORANGE, ORANGE_BG, "reserver, payer,\nbooking"),
        (72.5, "ocr",            PURPLE, PURPLE_BG, "passeport, visa,\nidentite"),
        (90,   "recommandation", TEAL,   TEAL_BG,   "recommandez,\nbudget, famille"),
    ]
    for cx, t, ec, fc, kw in intents:
        _box(ax, cx, 41, 17, 17, t, kw, ec=ec, fc=fc, tfs=18, sfs=14)
        ax.annotate('', xy=(cx, 49.5), xytext=(62, 70.5),
                    arrowprops=dict(arrowstyle='->', color=ec, lw=1.8,
                                    connectionstyle='arc3,rad=0.0'), zorder=5)

    # ── Module targets (cy=13, h=12, w=17) ───────────────────────────────────
    targets = [
        (10,   "RAG\ngeneral",       BLUE,   BLUE_BG),
        (27.5, "RAG\nprogramme",     GREEN,  GREEN_BG),
        (50,   "Gestionnaire\nresa", ORANGE, ORANGE_BG),
        (72.5, "Pipeline\nOCR",      PURPLE, PURPLE_BG),
        (90,   "LightGBM\n+ LLM",   TEAL,   TEAL_BG),
    ]
    for cx, t, ec, fc in targets:
        _box(ax, cx, 13, 17, 12, t, None, ec=ec, fc=fc, tfs=16)
        _varrow(ax, cx, 32.5, 19, ec)

    ax.text(50, 4, "Module cible active selon l'intention detectee",
            fontsize=16, style='italic', ha='center', va='center', color=GRAY)

    plt.savefig('schema_intent_classifier.png', dpi=200,
                facecolor=WHITE, bbox_inches=None)
    plt.close()
    print("Done: schema_intent_classifier.png")


# ─────────────────────────────────────────────────────────────────────────────
# 6. RAG COMPLET  —  figsize=(14,10)  →  2800×2000 px
# Full 4-step RAG: embed → Qdrant (2 variants) → Redis + Assemblage → Qwen
# ─────────────────────────────────────────────────────────────────────────────

def gen_rag_complet():
    BLUE   = '#1565C0';  BLUE_BG   = '#E3F2FD'
    GREEN  = '#2E7D32';  GREEN_BG  = '#E8F5E9'
    ORANGE = '#E65100';  ORANGE_BG = '#FFF3E0'
    TEAL   = '#004D40';  TEAL_BG   = '#E0F2F1'

    fig, ax = _setup(14, 10)

    ax.text(50, 97.5, "Pipeline RAG Complet — Rihla-AI",
            fontsize=36, fontweight='bold', ha='center', va='center', color=DARK)
    ax.text(50, 93, "4 etapes : Embedding → Recherche Qdrant → Contexte Redis → Generation Qwen 2.5 7B",
            fontsize=21, style='italic', ha='center', va='center', color=GRAY)

    # ── Etape 1: Encodage (band y=[76,91]) ────────────────────────────────────
    _bg(ax, 1, 76, 98, 15, BLUE, BLUE_BG, alpha=0.3)
    ax.text(50, 89.5, "Etape 1  —  Encodage de la question",
            fontsize=22, fontweight='bold', ha='center', color=BLUE, zorder=2)

    _box(ax, 24, 82, 26, 10, "Question", "Texte client",
         ec='#546E7A', fc='#ECEFF1', tfs=24, sfs=18)
    _box(ax, 68, 82, 38, 10, "nomic-embed-text",
         "Vecteur 768 dimensions",
         ec=BLUE, fc=BLUE_BG, tfs=24, sfs=18)
    _harrow(ax, 37, 49, 82, BLUE)

    # ── Etape 2: Recherche Qdrant (band y=[55,74]) ────────────────────────────
    _bg(ax, 1, 55, 98, 19, GREEN, GREEN_BG, alpha=0.3)
    ax.text(50, 72.5, "Etape 2  —  Recherche vectorielle Qdrant (selon intention)",
            fontsize=21, fontweight='bold', ha='center', color=GREEN, zorder=2)

    _box(ax, 22, 62, 36, 12, "Variante 1 — General",
         "Collection rihla_fr / rihla_ar\nTop-5 cosinus (seuil 0.3)",
         ec=GREEN, fc=GREEN_BG, tfs=21, sfs=17)
    _box(ax, 72, 62, 36, 12, "Variante 2 — Programme",
         "Filtre metadata: programme_id\nTop-5 dans la collection filtree",
         ec='#1B5E20', fc='#C8E6C9', tfs=21, sfs=17)

    # Arrows from nomic-embed bottom to both variants
    ax.annotate('', xy=(22, 68), xytext=(68, 77),
                arrowprops=dict(arrowstyle='->', color=GREEN, lw=2.5,
                                connectionstyle='arc3,rad=-0.2'), zorder=5)
    ax.annotate('', xy=(72, 68), xytext=(68, 77),
                arrowprops=dict(arrowstyle='->', color='#1B5E20', lw=2.5,
                                connectionstyle='arc3,rad=0.1'), zorder=5)

    # ── Etape 3: Redis + Assemblage (band y=[32,53]) ──────────────────────────
    _bg(ax, 1, 32, 98, 21, ORANGE, ORANGE_BG, alpha=0.3)
    ax.text(50, 51.5, "Etape 3  —  Assemblage du prompt",
            fontsize=22, fontweight='bold', ha='center', color=ORANGE, zorder=2)

    _box(ax, 22, 40, 34, 12, "Redis (TTL 24h)",
         "10 derniers echanges\ncle: session_id",
         ec=ORANGE, fc=ORANGE_BG, tfs=22, sfs=18)
    _box(ax, 75, 40, 38, 12, "Assemblage du prompt",
         "System + Historique Redis\n+ Contexte RAG + Question",
         ec='#BF360C', fc='#FBE9E7', tfs=21, sfs=17)

    # Both Qdrant variants → Assemblage (documents retrieved)
    ax.annotate('', xy=(75, 46), xytext=(22, 56),
                arrowprops=dict(arrowstyle='->', color=GREEN, lw=2.2,
                                connectionstyle='arc3,rad=0'), zorder=5)
    ax.annotate('', xy=(75, 46), xytext=(72, 56),
                arrowprops=dict(arrowstyle='->', color='#1B5E20', lw=2.2,
                                connectionstyle='arc3,rad=0.1'), zorder=5)
    # Redis → Assemblage (conversation history)
    _harrow(ax, 39, 56, 40, ORANGE)

    # ── Etape 4: Generation Qwen (band y=[6,30]) ──────────────────────────────
    _bg(ax, 1, 6, 98, 24, TEAL, TEAL_BG, alpha=0.3)
    ax.text(50, 28.5, "Etape 4  —  Generation Qwen 2.5 7B (Ollama)",
            fontsize=22, fontweight='bold', ha='center', color=TEAL, zorder=2)

    _box(ax, 28, 17, 40, 14, "Qwen 2.5 7B",
         "Modele local via Ollama\ntemperature=0.7  top_p=0.9  max_tokens=1024",
         ec=TEAL, fc=TEAL_BG, tfs=23, sfs=17)
    _box(ax, 78, 17, 34, 14, "Reponse + Redis",
         "Reponse factuelle\nHistorique += (Q, R)\nRenvoye via n8n",
         ec='#00695C', fc='#B2DFDB', tfs=21, sfs=17)
    _harrow(ax, 48, 61, 17, TEAL)

    # Assemblage → Qwen (short diagonal arrow)
    ax.annotate('', xy=(28, 24), xytext=(75, 34),
                arrowprops=dict(arrowstyle='->', color=TEAL, lw=2.5,
                                connectionstyle='arc3,rad=-0.15'), zorder=5)

    plt.savefig('schema_rag_complet.png', dpi=200,
                facecolor=WHITE, bbox_inches=None)
    plt.close()
    print("Done: schema_rag_complet.png")


# ─────────────────────────────────────────────────────────────────────────────
# 7. OCR DETAIL  —  figsize=(14,10)  →  2800×2000 px
# Image preprocessing → EasyOCR (ResNet→BiLSTM→CTC) + passporteye (MRZ) → JSON
# ─────────────────────────────────────────────────────────────────────────────

def gen_ocr_detail():
    ORANGE = '#E65100';  ORANGE_BG = '#FFF3E0'
    PURPLE = '#4A148C';  PURPLE_BG = '#F3E5F5'
    TEAL   = '#004D40';  TEAL_BG   = '#E0F2F1'

    fig, ax = _setup(14, 10)

    ax.text(50, 97, "Pipeline OCR Rihla-AI — Detail Technique",
            fontsize=36, fontweight='bold', ha='center', va='center', color=DARK)
    ax.text(50, 92.5, "Extraction automatique des champs d'un passeport via 3 composants complementaires",
            fontsize=22, style='italic', ha='center', va='center', color=GRAY)

    # Input
    _box(ax, 50, 84, 46, 12, "Image Passeport",
         "JPEG / PNG — numerise ou photographie",
         ec='#455A64', fc='#ECEFF1', tfs=28, sfs=20)

    # Preprocessing — h=12 (was 10) so subtitle fits inside
    _box(ax, 50, 67, 70, 12, "Pre-traitement",
         "Redimensionnement  |  Niveaux de gris  |  Debruitage (Gaussian)  |  Seuillage adaptatif",
         ec='#546E7A', fc='#CFD8DC', tfs=24, sfs=17)
    _varrow(ax, 50, 78, 73, '#546E7A')

    # T-junction split
    _varrow(ax, 50, 61, 58, '#546E7A')
    ax.plot([25, 75], [58, 58], color='#546E7A', lw=2.5, zorder=4)
    _varrow(ax, 25, 58, 53, ORANGE)
    _varrow(ax, 75, 58, 53, PURPLE)

    # Left: EasyOCR path
    _bg(ax, 2, 22, 44, 33, ORANGE, ORANGE_BG, alpha=0.30)
    ax.text(24, 55.5, "Moteur OCR principal", fontsize=19, fontweight='bold',
            ha='center', color=ORANGE, zorder=4)
    _box(ax, 24, 45, 40, 12, "EasyOCR",
         "ResNet → BiLSTM → CTC decoder",
         ec=ORANGE, fc=ORANGE_BG, tfs=24, sfs=18)
    _varrow(ax, 24, 39, 34, ORANGE)
    _box(ax, 24, 27, 40, 12, "Texte brut extrait",
         "Champs : nom, prenom,\ndate naiss., numero passeport",
         ec='#BF360C', fc='#FBE9E7', tfs=22, sfs=17)

    # Right: passporteye path
    _bg(ax, 54, 22, 44, 33, PURPLE, PURPLE_BG, alpha=0.30)
    ax.text(76, 55.5, "Zone MRZ ISO 9303", fontsize=19, fontweight='bold',
            ha='center', color=PURPLE, zorder=4)
    _box(ax, 76, 45, 40, 12, "passporteye",
         "Detection zone MRZ\n2 lignes x 44 caracteres",
         ec=PURPLE, fc=PURPLE_BG, tfs=24, sfs=18)
    _varrow(ax, 76, 39, 34, PURPLE)
    _box(ax, 76, 27, 40, 12, "Champs MRZ valides",
         "Nationalite, expiration\nChiffres de controle ISO",
         ec='#6A1B9A', fc='#EDE7F6', tfs=22, sfs=17)

    # Merge both paths → JSON output
    ax.annotate('', xy=(50, 19), xytext=(24, 21),
                arrowprops=dict(arrowstyle='->', color='#455A64', lw=2.5,
                                connectionstyle='angle,angleA=-90,angleB=180'), zorder=5)
    ax.annotate('', xy=(50, 19), xytext=(76, 21),
                arrowprops=dict(arrowstyle='->', color='#455A64', lw=2.5,
                                connectionstyle='angle,angleA=-90,angleB=0'), zorder=5)

    _box(ax, 50, 10, 90, 14, "Sortie JSON structuree",
         "nom  |  prenom  |  numero_passeport  |  date_naissance  |  date_expiration  |  nationalite",
         ec=TEAL, fc=TEAL_BG, tfs=24, sfs=17)

    plt.savefig('schema_ocr_detail.png', dpi=200,
                facecolor=WHITE, bbox_inches=None)
    plt.close()
    print("Done: schema_ocr_detail.png")


# ─────────────────────────────────────────────────────────────────────────────
# 8. LIGHTGBM PIPELINE  —  figsize=(14,9)  →  2800×1800 px
# Profile extraction → 22 features × 11 programmes → LightGBM → Top-3 → LLM
# ─────────────────────────────────────────────────────────────────────────────

def gen_lightgbm():
    TEAL   = '#004D40';  TEAL_BG   = '#E0F2F1'
    BLUE   = '#1565C0';  BLUE_BG   = '#E3F2FD'
    ORANGE = '#E65100';  ORANGE_BG = '#FFF3E0'
    GREEN  = '#2E7D32';  GREEN_BG  = '#E8F5E9'
    PURPLE = '#4A148C';  PURPLE_BG = '#F3E5F5'

    fig, ax = _setup(14, 9)

    ax.text(50, 96.5, "Pipeline de Recommandation LightGBM — Rihla-AI",
            fontsize=34, fontweight='bold', ha='center', va='center', color=DARK)
    ax.text(50, 91.5, "Du profil voyageur au Top-3 recommande : scoring LambdaRank sur 11 programmes",
            fontsize=21, style='italic', ha='center', va='center', color=GRAY)

    # ── Step 1: horizontal pipeline (y=76) ────────────────────────────────────
    _box(ax, 10, 76, 16, 14, "Message\nclient", "texte naturel",
         ec='#546E7A', fc='#ECEFF1', tfs=22, sfs=17, tdy=3.0)
    _box(ax, 33, 76, 24, 14, "Extraction\nprofil",
         "budget, nb_personnes\ntype_profil, preference",
         ec=BLUE, fc=BLUE_BG, tfs=22, sfs=17, tdy=3.0, sdy=-4.0)
    _box(ax, 60, 76, 26, 14, "22 features",
         "3 groupes de features\nProfil | Programme | Compat.",
         ec=ORANGE, fc=ORANGE_BG, tfs=22, sfs=17, tdy=2.8, sdy=-3.5)
    _box(ax, 85, 76, 20, 14, "LightGBM",
         "100 arbres LambdaRank\n< 5 ms",
         ec=TEAL, fc=TEAL_BG, tfs=23, sfs=17, tdy=2.8, sdy=-3.5)

    _harrow(ax, 18, 21, 76, BLUE)
    _harrow(ax, 45, 47, 76, ORANGE)
    _harrow(ax, 73, 75, 76, TEAL)

    # ── Scoring band (y=[38,63]) ──────────────────────────────────────────────
    _bg(ax, 2, 38, 96, 25, TEAL, TEAL_BG, alpha=0.25)
    ax.text(50, 61.5, "Scoring sur les 11 programmes disponibles",
            fontsize=20, fontweight='bold', ha='center', color=TEAL, zorder=2)

    prog_names = [
        "Istanbul\n+Cappadoce", "Dubai\nDecouverte", "Bali\nTranquillite",
        "Paris\nRomantique", "Maroc\nCulturel", "Egypte\nAntique",
        "Maldives\nLuxe", "Tokyo\nModerne", "New York\nVille", "Londres\nRoyale", "Rome\nHistoire"
    ]
    for i, pname in enumerate(prog_names):
        cx = 5.5 + i * 8.5
        _box(ax, cx, 49, 7.5, 16, pname, None, ec=TEAL, fc=TEAL_BG, tfs=12)

    # Single clean arrow from LightGBM → scoring band
    _varrow(ax, 85, 69, 63, TEAL)

    # ── Step 3: Top-3 + LLM (y=18) ────────────────────────────────────────────
    _box(ax, 28, 18, 34, 16, "Top-3 selectionne",
         "Tri decroissant des scores\nNDCG@5 = 1.0",
         ec=GREEN, fc=GREEN_BG, tfs=22, sfs=17)
    _box(ax, 74, 18, 36, 16, "Justification LLM",
         "Qwen 2.5 7B redige\nune explication personnalisee\npour chaque programme Top-3",
         ec=PURPLE, fc=PURPLE_BG, tfs=21, sfs=17)

    # Single clean arrow from scoring band → Top-3
    _varrow(ax, 28, 38, 26, GREEN)
    _harrow(ax, 45, 56, 18, PURPLE)

    ax.text(50, 5, "Reponse finale : Top-3 programmes avec justifications personnalisees",
            fontsize=19, fontweight='bold', ha='center', va='center',
            color=DARK, style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF8E1',
                      edgecolor='#F9A825', linewidth=1.5))

    plt.savefig('schema_lightgbm_pipeline.png', dpi=200,
                facecolor=WHITE, bbox_inches=None)
    plt.close()
    print("Done: schema_lightgbm_pipeline.png")


def gen_bdd_postgresql():
    """Simplified ERD: table names + relationships only, no field listings."""
    import matplotlib.patches as mp

    BLUE   = '#1565C0'; BLUE_L   = '#BBDEFB'
    GREEN  = '#2E7D32'; GREEN_L  = '#C8E6C9'
    ORANGE = '#BF360C'; ORANGE_L = '#FFE0B2'
    TEAL   = '#00695C'; TEAL_L   = '#B2DFDB'
    PURPLE = '#6A1B9A'; PURPLE_L = '#E1BEE7'
    SLATE  = '#37474F'; SLATE_L  = '#CFD8DC'

    W, H = 17, 7          # box width / height in data units
    NAME_FS = 13          # table name font size

    fig, ax = plt.subplots(figsize=(16, 12))
    plt.subplots_adjust(left=0.02, right=0.98, top=0.94, bottom=0.06)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor(WHITE)

    ax.text(50, 97, "Schéma de la Base de Données PostgreSQL – Rihla AI",
            ha='center', va='center', fontsize=15, fontweight='bold', color=DARK)

    def _tbl(cx, cy, label, hc, lc):
        x0, y0 = cx - W/2, cy - H/2
        ax.add_patch(mp.FancyBboxPatch((x0, y0), W, H,
                     boxstyle='round,pad=0.6', facecolor=lc,
                     edgecolor=hc, linewidth=2.5, zorder=3))
        ax.text(cx, cy, label, ha='center', va='center',
                fontsize=NAME_FS, fontweight='bold', color=hc, zorder=4,
                wrap=True)
        return dict(cx=cx, cy=cy, x0=x0, y0=y0)

    def _arrow(x1, y1, x2, y2, label, color, rad=0, ldy=1.2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2.0,
                                   connectionstyle=f'arc3,rad={rad}'), zorder=2)
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my + ldy, label, ha='center', va='bottom',
                    fontsize=9, fontweight='bold', color=color,
                    bbox=dict(fc='white', ec='none', pad=1), zorder=5)

    # ── positions (cx, cy)
    pos = {
        # Row 1  y=80
        'destinations':            (12,  80),
        'programme_destinations':  (35,  80),
        'programmes':              (60,  80),
        'hotels':                  (85,  80),
        # Row 2  y=60
        'conditions_visa':         (12,  60),
        'activites':               (85,  60),
        # Row 3  y=40
        'clients':                 (12,  40),
        'reservations':            (50,  40),
        'recommandations_log':     (85,  40),
        # Row 4  y=20
        'conversations':           (12,  20),
        'messages':                (50,  20),
        'administrateurs':         (85,  20),
    }

    colors = {
        'destinations': (BLUE, BLUE_L),
        'programme_destinations': (BLUE, BLUE_L),
        'conditions_visa': (BLUE, BLUE_L),
        'programmes': (GREEN, GREEN_L),
        'hotels': (GREEN, GREEN_L),
        'activites': (GREEN, GREEN_L),
        'clients': (ORANGE, ORANGE_L),
        'reservations': (ORANGE, ORANGE_L),
        'recommandations_log': (TEAL, TEAL_L),
        'conversations': (PURPLE, PURPLE_L),
        'messages': (PURPLE, PURPLE_L),
        'administrateurs': (SLATE, SLATE_L),
    }

    # ── draw all boxes
    b = {}
    for name, (cx, cy) in pos.items():
        hc, lc = colors[name]
        b[name] = _tbl(cx, cy, name.replace('_', '\n') if len(name) > 14 else name, hc, lc)

    # helper edge accessors
    def right(n, dy=0): return pos[n][0]+W/2, pos[n][1]+dy
    def left(n,  dy=0): return pos[n][0]-W/2, pos[n][1]+dy
    def top(n,   dx=0): return pos[n][0]+dx,  pos[n][1]+H/2
    def bot(n,   dx=0): return pos[n][0]+dx,  pos[n][1]-H/2

    # ── relationships
    # Row 1 horizontal chain
    _arrow(*right('destinations'), *left('programme_destinations'), '1:N', BLUE)
    _arrow(*right('programme_destinations'), *left('programmes'), 'N:1', BLUE)
    _arrow(*right('programmes'), *left('hotels'), '1:N', GREEN)

    # destinations → conditions_visa  (vertical)
    _arrow(*bot('destinations'), *top('conditions_visa'), '1:N', BLUE, ldy=0.8)

    # programmes → activites  (diagonal down-right)
    _arrow(*right('programmes', dy=-1), *top('activites', dx=-2), '1:N', GREEN, rad=0.2, ldy=0.8)

    # clients → reservations  (horizontal)
    _arrow(*right('clients'), *left('reservations'), '1:N', ORANGE)

    # reservations → programmes  (straight up through empty middle space)
    _arrow(*top('reservations', dx=2), *bot('programmes', dx=2), 'N:1', ORANGE, rad=0, ldy=0.8)

    # clients → recommandations_log  (horizontal, offset up slightly)
    _arrow(*right('clients', dy=1.5), *left('recommandations_log', dy=1.5), '1:N', TEAL, rad=-0.18, ldy=0.8)

    # clients → conversations  (vertical)
    _arrow(*bot('clients'), *top('conversations'), '1:N', PURPLE, ldy=0.8)

    # conversations → messages  (horizontal)
    _arrow(*right('conversations'), *left('messages'), '1:N', PURPLE)

    # ── legend
    legend_items = [
        (BLUE,   'Géographie / Référentiel'),
        (GREEN,  'Programmes / Contenus'),
        (ORANGE, 'Clients / Réservations'),
        (TEAL,   'Logs IA'),
        (PURPLE, 'Conversations'),
        (SLATE,  'Administration'),
    ]
    for i, (col, lbl) in enumerate(legend_items):
        lx = 1.5 + i * 16.5
        ax.add_patch(mp.Rectangle((lx, 1.2), 3, 2.2, facecolor=col, zorder=6))
        ax.text(lx + 3.8, 2.3, lbl, va='center', fontsize=8.5,
                color='#37474F', zorder=6)

    plt.savefig('schema_bdd_postgresql.png', dpi=180,
                facecolor=WHITE, bbox_inches=None)
    plt.close()
    print("Done: schema_bdd_postgresql.png")


if __name__ == '__main__':
    gen_rag()
    gen_ocr()
    gen_arch()
    gen_workflow()
    gen_intent()
    gen_rag_complet()
    gen_ocr_detail()
    gen_lightgbm()
    gen_bdd_postgresql()
    print("\nAll 9 schemas generated.")
