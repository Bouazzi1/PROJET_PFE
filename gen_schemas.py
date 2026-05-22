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


# ─────────────────────────────────────────────────────────────────────────────
# 4. WORKFLOW CONVERSATIONNEL  —  figsize=(14,8)  →  2800×1600 px
# Left-to-right: WhatsApp/Email → n8n → FastAPI → Intent → Routing → modules
# ─────────────────────────────────────────────────────────────────────────────

def gen_workflow():
    SLATE  = '#455A64';  SLATE_BG  = '#ECEFF1'
    BLUE   = '#1565C0';  BLUE_BG   = '#E3F2FD'
    GREEN  = '#2E7D32';  GREEN_BG  = '#E8F5E9'
    ORANGE = '#E65100';  ORANGE_BG = '#FFF3E0'
    PURPLE = '#4A148C';  PURPLE_BG = '#F3E5F5'
    TEAL   = '#004D40';  TEAL_BG   = '#E0F2F1'
    RED    = '#B71C1C';  RED_BG    = '#FFCDD2'

    fig, ax = _setup(14, 8)

    ax.text(50, 96.5, "Workflow de traitement d'un message Rihla-AI",
            fontsize=36, fontweight='bold', ha='center', va='center', color=DARK)
    ax.text(50, 91.5, "Du canal d'entree a la reponse : classification d'intentions et routage",
            fontsize=22, style='italic', ha='center', va='center', color=GRAY)

    # ── Row 1: Input channels (y=78) ─────────────────────────────────────────
    _box(ax, 15, 78, 24, 12, "WhatsApp", "WAHA API\nWebhook n8n",
         ec='#1B5E20', fc='#C8E6C9', tfs=26, sfs=18)
    _box(ax, 42, 78, 24, 12, "Email", "IMAP Reception\nWebhook n8n",
         ec=RED, fc=RED_BG, tfs=26, sfs=18)

    # n8n (center top)
    _box(ax, 71, 78, 22, 12, "n8n", "Orchestration\nRouting webhook",
         ec=BLUE, fc=BLUE_BG, tfs=26, sfs=18)

    # FastAPI
    _box(ax, 88, 78, 18, 12, "FastAPI", "POST /conversations\n/ocr  /recommend",
         ec=GREEN, fc=GREEN_BG, tfs=24, sfs=17)

    # Arrows row 1
    _harrow(ax, 27, 30, 78, '#1B5E20')
    _harrow(ax, 54, 60, 78, BLUE)
    _harrow(ax, 82, 79, 78, GREEN)

    # ── Intent Classifier (center, y=52) ─────────────────────────────────────
    _box(ax, 50, 52, 34, 14, "Classificateur d'intentions",
         "Analyse mots-cles  |  5 classes",
         ec=ORANGE, fc=ORANGE_BG, tfs=24, sfs=18)

    # Arrow from FastAPI down to Intent
    ax.annotate('', xy=(50, 59), xytext=(88, 72),
                arrowprops=dict(arrowstyle='->', color=ORANGE, lw=2.5,
                                connectionstyle='angle,angleA=0,angleB=90'), zorder=5)

    # ── 3 output modules (y=25) ──────────────────────────────────────────────
    modules = [
        (18,  "RAG",           "Qwen 2.5 7B\n+ Qdrant\ngeneral / programme",
         BLUE,   BLUE_BG),
        (50,  "OCR",           "EasyOCR\n+ passporteye\nextraction passeport",
         PURPLE, PURPLE_BG),
        (82,  "Recommandeur",  "LightGBM\n22 features\nTop-3 programmes",
         TEAL,   TEAL_BG),
    ]
    for cx, t, s, ec, fc in modules:
        _box(ax, cx, 25, 28, 24, t, s, ec=ec, fc=fc, tfs=25, sfs=18)

    # Arrows from Intent to modules
    for mx in [18, 50, 82]:
        ax.annotate('', xy=(mx, 37), xytext=(50, 45),
                    arrowprops=dict(arrowstyle='->', color=ORANGE, lw=2.2,
                                    connectionstyle='arc3,rad=0.0'), zorder=5)

    # Response arrow back (label)
    ax.text(50, 10, "Reponse renvoyee via n8n → WhatsApp / Email",
            fontsize=20, fontweight='bold', ha='center', va='center',
            color=SLATE, style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=SLATE_BG,
                      edgecolor=SLATE, linewidth=1.5))

    plt.savefig('schema_workflow_conversationnel.png', dpi=200,
                facecolor=WHITE, bbox_inches=None)
    plt.close()
    print("Done: schema_workflow_conversationnel.png")


# ─────────────────────────────────────────────────────────────────────────────
# 5. INTENT CLASSIFIER  —  figsize=(13,8)  →  2600×1600 px
# text → normalize → 5 keyword dicts → intent → routing
# ─────────────────────────────────────────────────────────────────────────────

def gen_intent():
    ORANGE = '#E65100';  ORANGE_BG = '#FFF3E0'
    BLUE   = '#1565C0';  BLUE_BG   = '#E3F2FD'
    GREEN  = '#2E7D32';  GREEN_BG  = '#E8F5E9'
    PURPLE = '#4A148C';  PURPLE_BG = '#F3E5F5'
    TEAL   = '#004D40';  TEAL_BG   = '#E0F2F1'
    RED    = '#B71C1C';  RED_BG    = '#FFCDD2'

    fig, ax = _setup(13, 8)

    ax.text(50, 96, "Classificateur d'intentions Rihla-AI",
            fontsize=36, fontweight='bold', ha='center', va='center', color=DARK)
    ax.text(50, 91, "Normalisation → Detection par mots-cles → Routage vers le module cible",
            fontsize=22, style='italic', ha='center', va='center', color=GRAY)

    # Stage 1: Input
    _box(ax, 8, 68, 12, 12, "Message\nclient", None,
         ec='#546E7A', fc='#ECEFF1', tfs=22, sfs=0)

    # Stage 2: Normalize
    _box(ax, 25, 68, 18, 12, "Normalisation",
         "minuscules\nsans accents",
         ec='#455A64', fc='#CFD8DC', tfs=22, sfs=18)

    # Stage 3: Keyword matching
    _box(ax, 50, 68, 24, 12, "Detection\nmots-cles",
         "5 dictionnaires\npar classe",
         ec=ORANGE, fc=ORANGE_BG, tfs=22, sfs=18)

    _harrow(ax, 14, 16, 68, '#546E7A')
    _harrow(ax, 34, 38, 68, '#455A64')

    # Stage 4: 5 intent boxes
    intents = [
        (10,  "general",        BLUE,   BLUE_BG,   "bonjour, aide,\ninformation"),
        (27,  "programme",      GREEN,  GREEN_BG,  "programme, voyage,\ndestination"),
        (50,  "reservation",    ORANGE, ORANGE_BG, "reserver, payer,\nbooking"),
        (73,  "ocr",            PURPLE, PURPLE_BG, "passeport, visa,\nidentite"),
        (90,  "recommandation", TEAL,   TEAL_BG,   "recommandez,\nbudget, famille"),
    ]
    for cx, t, ec, fc, kw in intents:
        _box(ax, cx, 36, 15, 18, t, kw, ec=ec, fc=fc, tfs=19, sfs=15)
        ax.annotate('', xy=(cx, 45), xytext=(50, 62),
                    arrowprops=dict(arrowstyle='->', color=ec, lw=2.0,
                                    connectionstyle='arc3,rad=0.0'), zorder=5)

    # Module targets
    targets = [
        (10,  "RAG\ngeneral",     BLUE,   BLUE_BG),
        (27,  "RAG\nprogramme",   GREEN,  GREEN_BG),
        (50,  "Gestionnaire\nresa", ORANGE, ORANGE_BG),
        (73,  "Pipeline\nOCR",    PURPLE, PURPLE_BG),
        (90,  "LightGBM\n+ LLM",  TEAL,   TEAL_BG),
    ]
    for cx, t, ec, fc in targets:
        _box(ax, cx, 10, 15, 12, t, None, ec=ec, fc=fc, tfs=17, sfs=0)
        _varrow(ax, cx, 27, 16, ec)

    ax.text(50, 3.5, "Module cible active selon l'intention detectee",
            fontsize=17, style='italic', ha='center', va='center', color=GRAY)

    plt.savefig('schema_intent_classifier.png', dpi=200,
                facecolor=WHITE, bbox_inches=None)
    plt.close()
    print("Done: schema_intent_classifier.png")


# ─────────────────────────────────────────────────────────────────────────────
# 6. RAG COMPLET  —  figsize=(14,10)  →  2800×2000 px
# Full 4-step RAG with Redis memory + 2 variants (general / programme)
# ─────────────────────────────────────────────────────────────────────────────

def gen_rag_complet():
    BLUE   = '#1565C0';  BLUE_BG   = '#E3F2FD'
    GREEN  = '#2E7D32';  GREEN_BG  = '#E8F5E9'
    ORANGE = '#E65100';  ORANGE_BG = '#FFF3E0'
    TEAL   = '#004D40';  TEAL_BG   = '#E0F2F1'
    RED    = '#B71C1C';  RED_BG    = '#FFCDD2'

    fig, ax = _setup(14, 10)

    ax.text(50, 97, "Pipeline RAG Complet — Rihla-AI",
            fontsize=36, fontweight='bold', ha='center', va='center', color=DARK)
    ax.text(50, 92.5, "4 etapes : Embedding → Recherche Qdrant → Contexte Redis → Generation Qwen 2.5 7B",
            fontsize=22, style='italic', ha='center', va='center', color=GRAY)

    # ── Step 1: Question input + embedding ───────────────────────────────────
    _bg(ax, 1, 75, 98, 16, BLUE, BLUE_BG, alpha=0.3)
    ax.text(50, 89.5, "Etape 1  —  Encodage de la question",
            fontsize=22, fontweight='bold', ha='center', color=BLUE, zorder=2)

    _box(ax, 15, 81, 22, 10, "Question", "Texte client",
         ec='#546E7A', fc='#ECEFF1', tfs=24, sfs=18)
    _box(ax, 50, 81, 28, 10, "nomic-embed-text",
         "Vecteur 768 dimensions",
         ec=BLUE, fc=BLUE_BG, tfs=22, sfs=18)
    _harrow(ax, 26, 36, 81, BLUE)

    # ── Step 2: Qdrant search (2 variants) ───────────────────────────────────
    _bg(ax, 1, 55, 98, 18, GREEN, GREEN_BG, alpha=0.3)
    ax.text(50, 71.5, "Etape 2  —  Recherche vectorielle Qdrant",
            fontsize=22, fontweight='bold', ha='center', color=GREEN, zorder=2)

    _box(ax, 20, 62, 32, 10, "Variante 1 — General",
         "Collection rihla_fr / rihla_ar\nTop-5 cosinus (seuil 0.3)",
         ec=GREEN, fc=GREEN_BG, tfs=21, sfs=17)
    _box(ax, 70, 62, 32, 10, "Variante 2 — Programme",
         "Filtre metadata: programme_id\nTop-5 dans la collection filtree",
         ec='#1B5E20', fc='#C8E6C9', tfs=21, sfs=17)

    ax.annotate('', xy=(20, 67), xytext=(50, 76),
                arrowprops=dict(arrowstyle='->', color=GREEN, lw=2.5,
                                connectionstyle='arc3,rad=-0.15'), zorder=5)
    ax.annotate('', xy=(70, 67), xytext=(50, 76),
                arrowprops=dict(arrowstyle='->', color=GREEN, lw=2.5,
                                connectionstyle='arc3,rad=0.15'), zorder=5)

    # ── Step 3: Redis context ─────────────────────────────────────────────────
    _bg(ax, 1, 35, 98, 18, ORANGE, ORANGE_BG, alpha=0.3)
    ax.text(50, 51.5, "Etape 3  —  Historique conversationnel Redis",
            fontsize=22, fontweight='bold', ha='center', color=ORANGE, zorder=2)

    _box(ax, 25, 42, 34, 10, "Redis (TTL 24h)",
         "10 derniers echanges\ncle: session_id",
         ec=ORANGE, fc=ORANGE_BG, tfs=22, sfs=18)
    _box(ax, 72, 42, 38, 10, "Assemblage du prompt",
         "System + Historique + Contexte RAG\n+ Question actuelle",
         ec='#BF360C', fc='#FBE9E7', tfs=21, sfs=17)
    _harrow(ax, 42, 53, 42, ORANGE)

    ax.annotate('', xy=(25, 47), xytext=(20, 57),
                arrowprops=dict(arrowstyle='->', color=ORANGE, lw=2.2,
                                connectionstyle='arc3,rad=0.15'), zorder=5)
    ax.annotate('', xy=(72, 47), xytext=(70, 57),
                arrowprops=dict(arrowstyle='->', color=ORANGE, lw=2.2,
                                connectionstyle='arc3,rad=-0.15'), zorder=5)

    # ── Step 4: LLM generation ────────────────────────────────────────────────
    _bg(ax, 1, 8, 98, 25, TEAL, TEAL_BG, alpha=0.3)
    ax.text(50, 31.5, "Etape 4  —  Generation Qwen 2.5 7B (Ollama)",
            fontsize=22, fontweight='bold', ha='center', color=TEAL, zorder=2)

    _box(ax, 25, 18, 34, 16, "Qwen 2.5 7B",
         "Modele local via Ollama\ntemperature=0.7  top_p=0.9\nmax_tokens=1024",
         ec=TEAL, fc=TEAL_BG, tfs=23, sfs=18)
    _box(ax, 75, 18, 34, 16, "Reponse + mise a jour Redis",
         "Reponse factuelle\nHistorique += (question, reponse)\nRenvoye via n8n au canal",
         ec='#00695C', fc='#B2DFDB', tfs=20, sfs=17)
    _harrow(ax, 42, 58, 18, TEAL)

    ax.annotate('', xy=(25, 26), xytext=(72, 37),
                arrowprops=dict(arrowstyle='->', color=TEAL, lw=2.5,
                                connectionstyle='angle,angleA=0,angleB=90'), zorder=5)

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
    BLUE   = '#1565C0';  BLUE_BG   = '#E3F2FD'

    fig, ax = _setup(14, 10)

    ax.text(50, 97, "Pipeline OCR Rihla-AI — Detail Technique",
            fontsize=36, fontweight='bold', ha='center', va='center', color=DARK)
    ax.text(50, 92.5, "Extraction automatique des champs d'un passeport via 3 composants complementaires",
            fontsize=22, style='italic', ha='center', va='center', color=GRAY)

    # Input
    _box(ax, 50, 84, 46, 12, "Image Passeport",
         "JPEG / PNG — numerise ou photographie",
         ec='#455A64', fc='#ECEFF1', tfs=28, sfs=20)

    # Preprocessing
    _box(ax, 50, 68, 60, 10, "Pre-traitement",
         "Redimensionnement  |  Niveaux de gris  |  Debruitage (Gaussian)  |  Seuillage adaptatif",
         ec='#546E7A', fc='#CFD8DC', tfs=22, sfs=17)
    _varrow(ax, 50, 78, 73, '#546E7A')

    # Split to 2 parallel paths
    _varrow(ax, 50, 63, 60, '#546E7A')
    ax.plot([25, 75], [60, 60], color='#546E7A', lw=2.5, zorder=4)
    _varrow(ax, 25, 60, 55, ORANGE)
    _varrow(ax, 75, 60, 55, PURPLE)

    # Left: EasyOCR path
    _bg(ax, 2, 25, 44, 32, ORANGE, ORANGE_BG, alpha=0.30)
    ax.text(24, 57.5, "Moteur OCR principal", fontsize=19, fontweight='bold',
            ha='center', color=ORANGE, zorder=4)
    _box(ax, 24, 47, 40, 10, "EasyOCR",
         "ResNet → BiLSTM → CTC decoder",
         ec=ORANGE, fc=ORANGE_BG, tfs=23, sfs=18)
    _varrow(ax, 24, 42, 37, ORANGE)
    _box(ax, 24, 30, 40, 10, "Texte brut extrait",
         "Champs : nom, prenom,\ndate naiss., numero passeport",
         ec='#BF360C', fc='#FBE9E7', tfs=21, sfs=17)

    # Right: passporteye path
    _bg(ax, 54, 25, 44, 32, PURPLE, PURPLE_BG, alpha=0.30)
    ax.text(76, 57.5, "Zone MRZ ISO 9303", fontsize=19, fontweight='bold',
            ha='center', color=PURPLE, zorder=4)
    _box(ax, 76, 47, 40, 10, "passporteye",
         "Detection zone MRZ\n2 lignes x 44 caracteres",
         ec=PURPLE, fc=PURPLE_BG, tfs=23, sfs=18)
    _varrow(ax, 76, 42, 37, PURPLE)
    _box(ax, 76, 30, 40, 10, "Champs MRZ valides",
         "Nationalite, expiration\nChiffres de controle ISO",
         ec='#6A1B9A', fc='#EDE7F6', tfs=21, sfs=17)

    # Merge → JSON output
    ax.annotate('', xy=(50, 22), xytext=(24, 25),
                arrowprops=dict(arrowstyle='->', color='#455A64', lw=2.5,
                                connectionstyle='angle,angleA=-90,angleB=180'), zorder=5)
    ax.annotate('', xy=(50, 22), xytext=(76, 25),
                arrowprops=dict(arrowstyle='->', color='#455A64', lw=2.5,
                                connectionstyle='angle,angleA=-90,angleB=0'), zorder=5)

    _box(ax, 50, 12, 90, 14, "Sortie JSON structuree",
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

    # Step 1: Message → Profile extraction
    _box(ax, 10, 74, 16, 14, "Message\nclient",
         "texte naturel",
         ec='#546E7A', fc='#ECEFF1', tfs=22, sfs=17)
    _box(ax, 33, 74, 24, 14, "Extraction\nprofil",
         "budget, nb_personnes\ntype_profil, preference",
         ec=BLUE, fc=BLUE_BG, tfs=22, sfs=17)
    _harrow(ax, 18, 21, 74, BLUE)

    # Step 2: 22 features
    _box(ax, 60, 74, 26, 14, "22 features",
         "Groupe 1: profil voyageur\nGroupe 2: attributs programme\nGroupe 3: compatibilite",
         ec=ORANGE, fc=ORANGE_BG, tfs=22, sfs=16)
    _harrow(ax, 45, 47, 74, ORANGE)

    # Step 3: LightGBM
    _box(ax, 85, 74, 20, 14, "LightGBM",
         "100 arbres\nLambdaRank\n< 5 ms",
         ec=TEAL, fc=TEAL_BG, tfs=23, sfs=17)
    _harrow(ax, 73, 75, 74, TEAL)

    # 11 programmes scores (middle band)
    _bg(ax, 2, 38, 96, 24, TEAL, TEAL_BG, alpha=0.25)
    ax.text(50, 60.5, "Scoring sur les 11 programmes disponibles",
            fontsize=20, fontweight='bold', ha='center', color=TEAL, zorder=2)

    prog_names = [
        "Istanbul\n+Cappadoce", "Dubai\nDecouverte", "Bali\nTranquillite",
        "Paris\nRomantique", "Maroc\nCulturel", "Egypte\nAntique",
        "Maldives\nLuxe", "Tokyo\nModerne", "New York\nVille", "Londres\nRoyale", "Rome\nHistoire"
    ]
    spacing = 8.5
    start = 5.5
    for i, pname in enumerate(prog_names):
        cx = start + i * spacing
        _box(ax, cx, 48, 7.5, 14, pname, None,
             ec=TEAL, fc=TEAL_BG, tfs=12, sfs=0)
        ax.annotate('', xy=(cx, 55), xytext=(85, 67),
                    arrowprops=dict(arrowstyle='->', color=TEAL, lw=1.2,
                                    connectionstyle='arc3,rad=0.0'), zorder=5)

    # Step 4: Top-3 + LLM justification
    _box(ax, 28, 18, 32, 16, "Top-3 selectionne",
         "Tri decroissant des scores\nSeuil de pertinence NDCG@5=1.0",
         ec=GREEN, fc=GREEN_BG, tfs=22, sfs=17)
    _box(ax, 73, 18, 36, 16, "Justification LLM",
         "Qwen 2.5 7B redige\nune explication personnalisee\npour chaque programme Top-3",
         ec=PURPLE, fc=PURPLE_BG, tfs=21, sfs=17)

    # Top-3 arrows from bottom of score band
    ax.annotate('', xy=(28, 26), xytext=(50, 38),
                arrowprops=dict(arrowstyle='->', color=GREEN, lw=2.5,
                                connectionstyle='arc3,rad=-0.2'), zorder=5)
    _harrow(ax, 44, 55, 18, PURPLE)

    # Final response
    ax.text(50, 5, "Reponse finale : Top-3 programmes avec justifications personnalisees",
            fontsize=19, fontweight='bold', ha='center', va='center',
            color=DARK, style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF8E1',
                      edgecolor='#F9A825', linewidth=1.5))

    plt.savefig('schema_lightgbm_pipeline.png', dpi=200,
                facecolor=WHITE, bbox_inches=None)
    plt.close()
    print("Done: schema_lightgbm_pipeline.png")


if __name__ == '__main__':
    gen_rag()
    gen_ocr()
    gen_arch()
    gen_workflow()
    gen_intent()
    gen_rag_complet()
    gen_ocr_detail()
    gen_lightgbm()
    print("\nAll 8 schemas generated.")
