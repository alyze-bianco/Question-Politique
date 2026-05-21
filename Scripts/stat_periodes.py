
# Ce script permet de faire des statistiques sur les types d'événements par titre source, en se concentrant 
# sur les 6 types cibles. Il lit le CSV, normalise les types, agrège les données, puis affiche un graphique 
# à barres empilées avec un tableau de pourcentages en dessous. Les types non reconnus sont comptabilisés et 
# affichés à la fin pour aider au debug.

import csv
import os
import unicodedata
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import numpy as np

csv_path = r"\\wsl.localhost\Ubuntu\home\aly\GithubLinux\test-\Enrichi\evenement_histo_csv\CSV\CSV_type2.csv"
out_dir = os.path.dirname(csv_path)

if not os.path.isfile(csv_path):
    print(f"Fichier introuvable : {csv_path}")
    raise SystemExit(1)

TYPES_CIBLES = [
    "contemporain à l'auteur",    
    "moyen âge tardif",
    "haut moyen âge",
    "antiquité classique",
    "antiquité biblique",
    "mythologie",
    
    
    
    
    
    
]

def strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )

def normalize_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.replace("’", "'")
    s = strip_accents(s)
    s = " ".join(s.split())
    return s

CANON = {normalize_text(t): t for t in TYPES_CIBLES}

ALIASES = {
    normalize_text("antiquite biblique"): "antiquité biblique",
    normalize_text("antiquite classique"): "antiquité classique",
    normalize_text("haut moyen age"): "haut moyen âge",
    normalize_text("moyen age tardif"): "moyen âge tardif",    
    normalize_text("contemporain a l'auteur"): "contemporain à l'auteur",
    normalize_text("contemporain a l auteur"): "contemporain à l'auteur",
}

def map_type(raw: str):
    key = normalize_text(raw)
    if key in CANON:
        return CANON[key]
    if key in ALIASES:
        return ALIASES[key]
    return None

def normalize_header(h: str) -> str:
    """
    Normalise un nom de colonne :
    - enlève BOM éventuel
    - strip espaces
    - lowercase
    """
    if h is None:
        return ""
    return h.replace("\ufeff", "").strip().lower()

# === Lecture + agrégation ===
resultats = defaultdict(Counter)
ignored_types = Counter()

# IMPORTANT : utf-8-sig enlève le BOM au début du fichier
with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f, delimiter=";")

    if not reader.fieldnames:
        print("CSV vide ou en-tête introuvable.")
        raise SystemExit(1)

    # map en-têtes normalisés -> en-têtes réels
    header_map = {normalize_header(h): h for h in reader.fieldnames}

    # Colonnes attendues (chez toi : Titre source et Type)
    col_source = header_map.get("titre source")
    col_type = header_map.get("type")

    if not col_source:
        print("Colonne 'Titre source' introuvable après normalisation.")
        print(f"Colonnes disponibles : {reader.fieldnames}")
        raise SystemExit(1)

    if not col_type:
        print("Colonne 'Type' introuvable après normalisation.")
        print(f"Colonnes disponibles : {reader.fieldnames}")
        raise SystemExit(1)

    for row in reader:
        titre_source = (row.get(col_source) or "").strip() or "source_inconnue"
        raw_type = row.get(col_type, "")

        type_canon = map_type(raw_type)
        if type_canon is None:
            ignored_types[normalize_text(raw_type) or "inconnu"] += 1
            continue

        resultats[titre_source][type_canon] += 1

if not resultats:
    print("Aucun événement reconnu dans les 6 types cibles. Vérifie les valeurs de la colonne Type.")
    raise SystemExit(1)

# === Statistiques ===
print("=== STATISTIQUES (par Titre source, uniquement les 6 types) ===\n")
for source, counter in resultats.items():
    total = sum(counter.values())
    print(f"{source} (total types cibles: {total})")
    for t in TYPES_CIBLES:
        n = counter.get(t, 0)
        pct = (n / total * 100) if total else 0
        print(f"  - {t}: {n} ({pct:.1f}%)")
    print()

# Debug : types ignorés
if ignored_types:
    total_ignored = sum(ignored_types.values())
    print(f"=== TYPES IGNORÉS (non reconnus) : {total_ignored} lignes ===")
    for t, n in ignored_types.most_common(30):
        print(f"  - '{t}': {n}")
    print("Si un type ignoré doit correspondre à un des 6 types, ajoute-le dans ALIASES.\n")

    PAGES = {
    "Question Politique (1569)": "48",
    "Le réveil matin (1574)": "390",
    "Du droit des magistrats (1574)": "84",
    "Le Politique (1576)": "80",
    "Discours Politiques des diverses puissances (1578)": "147",
    "De la puissance legitime (1581)": "271",
    "La Gaule Françoise (1574)": "254",
}

# === Graphique : barres empilées + tableau ===
# ordre voulu des œuvres
ORDER_SOURCES = [
    "Question Politique (1569)",
    "Du droit des magistrats (1574)",
    "La Gaule Françoise (1574)",
    "Le Réveille-matin (1574)",
    "Le Politique (1576)",
    "Discours politiques (1578)",
    "De la puissance legitime (1581)",
]

# applique l'ordre demandé
sources = [s for s in ORDER_SOURCES if s in resultats]

# ajoute éventuellement d'autres sources non listées
sources += [s for s in resultats.keys() if s not in ORDER_SOURCES]
types = TYPES_CIBLES[:]

data = np.array([[resultats[s].get(t, 0) for t in types] for s in sources])

# Pourcentages
totals = data.sum(axis=1)
pct = np.divide(
    data,
    totals[:, None],
    out=np.zeros_like(data, dtype=float),
    where=totals[:, None] != 0
) * 100

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.size"] = 11

# Figure avec espace en bas pour la table
fig, ax = plt.subplots(figsize=(18, 10))

x = np.arange(len(sources))
bottom = np.zeros(len(sources), dtype=int)

# barres empilées
for j, t in enumerate(types):
    ax.bar(
        x,
        data[:, j],
        bottom=bottom,
        label=t,
        edgecolor="white",
        linewidth=0.8
    )
    bottom += data[:, j]

# Axes
ax.set_xlabel("Œuvres du corpus monarchomaque")
ax.set_ylabel("Nombre d'événements")
ax.set_title(
    "Distribution des types d’événements dans le corpus monarchomaque",
    fontsize=18,        # taille
    fontweight="bold",  # gras
    pad=20              # espace au-dessus du graphe
)
ax.set_xticks(x)
ax.set_xticklabels(sources, rotation=45, ha="right")

ax.legend(
    loc="upper left",
    bbox_to_anchor=(1.02, 1.0),  # décale à droite
    frameon=True
)

# ====================================================
# TABLEAU DES POURCENTAGES (compact sous le graphe)
# ====================================================

TYPE_LABELS = {
    "antiquité biblique": "Antiquité Biblique",
    "antiquité classique": "Antiquité Classique",
    "haut moyen âge": "Haut Moyen Âge",
    "moyen âge tardif": "Moyen Âge Tardif",
    "contemporain à l'auteur": "Contemporain à l'auteur",
    "mythologie": "Mythologie",
}

# Colonnes du tableau (sans nombre de pages)
col_labels_short = [TYPE_LABELS[t] for t in types]

# Données du tableau (%)
pct_str = [
    [f"{pct[i, j]:.1f}" for j in range(len(types))]
    for i in range(len(sources))
]

plt.subplots_adjust(bottom=0.40)   # espace sous le graphique

table = plt.table(
    cellText=pct_str,
    rowLabels=sources,
    colLabels=col_labels_short,
    cellLoc="center",
    rowLoc="center",
    bbox=[0.0, -0.90, 1.0, 0.32]  # sous le graphique
)

table.auto_set_font_size(False)
table.set_fontsize(8)
table.scale(1.0, 0.9)

# style léger
for (_, _), cell in table.get_celld().items():
    cell.set_linewidth(0.3)

plt.tight_layout()

out_png = os.path.join(out_dir, "statistiques_6_types_par_titre_source_tableau.png")
plt.savefig(out_png, dpi=300, bbox_inches="tight")
print(f"Graphique sauvegardé sous : {out_png}")

plt.show()