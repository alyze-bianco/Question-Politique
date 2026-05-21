# Ce script permet de calculer les distances temporelles entre la date d'un ou plusieurs écrits et les exempla utilisés par leurs auteurs.
# Il utilise une visualitation en diagramme en violon pour montrer la distribution de ces distances, 
# ainsi que des statistiques de base (moyenne, médiane) pour chaque ouvrage.

import csv
import os
import re
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np



# =========================
# Réglages
# =========================

SCRIPT_DIR = r"\\wsl.localhost\Ubuntu\home\aly\GithubLinux\test-\Enrichi\evenement_histo_csv"
COMBINED_CSV = r"\\wsl.localhost\Ubuntu\home\aly\GithubLinux\test-\Enrichi\evenement_histo_csv\CSV\CSV_type2.csv"
METADATA_FILENAME = "metadata.csv.back"

CSV_DELIMITER = ";"

BOOK_KEY_COLUMN = "Titre source"   # ✅ colonne qui identifie l’ouvrage dans le CSV agrégé
EVENT_DATE_COLUMN = "Date_stat"    # ✅ colonne de date à utiliser uniquement

# Correspondance entre "Titre source" (CSV agrégé)
# et "file_name" du metadata.csv.back
TITLE_TO_FILEKEY = {
    "Question Politique (1569)": "question_politique_1569",
    "Le Réveille-matin (1574)": "reveille_matin_1574",
    "Du droit des magistrats (1574)": "droit_des_magistrats_1574",
    "Le Politique (1576)" : "le_politique_1576",
    "Discours politiques (1578)" : "discours_politiques_1578",
    "De la puissance légitime (1581)" : "puissance_legitime_1581",
    "La Gaule Françoise (1574)" : "gaule_francoise_1574",
}


# =========================
# Fonctions utilitaires
# =========================

def extract_year_from_date(date_str):
    if not date_str:
        return None
    match = re.search(r"\b(\d{4})\b", str(date_str))
    return int(match.group(1)) if match else None


def parse_event_date(date_str):
    if not date_str:
        return None

    s = str(date_str).strip()
    if not s:
        return None

    number=int(s) if s.split("-", 1)[-1].isdecimal() else None
    if number is not None:
        return number

    # périodes 1500-1600
    if "-" in s:
        years = re.findall(r"\b(\d{4})\b", s)
        if len(years) >= 2:
            return (int(years[0]) + int(years[1])) // 2
        if len(years) == 1:
            return int(years[0])

    # approximations
    if "vers" in s.lower() or "ca." in s.lower() or "circa" in s.lower():
        return extract_year_from_date(s)
    #try parse int directly

    return extract_year_from_date(s)


def normalize_key(s):
    """Normalise une clé pour maximiser les correspondances avec metadata."""
    if s is None:
        return ""
    s = str(s).strip().lower()
    s = s.replace("\\", "/")
    s = s.replace("data/", "")
    if s.endswith(".csv"):
        s = s[:-4]
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


# =========================
# Charger metadata
# =========================

metadata_path = os.path.join(SCRIPT_DIR, METADATA_FILENAME)
books_data = {}  # clé normalisée -> infos

try:
    with open(metadata_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_file_name = row.get("file_name", "")
            title = (row.get("title") or "").strip()
            author = (row.get("author") or "").strip()
            date_year = extract_year_from_date(row.get("date"))

            if not raw_file_name or not date_year:
                continue

            key = normalize_key(raw_file_name)
            books_data[key] = {"title": title, "date": date_year, "author": author}

except FileNotFoundError:
    print(f"Fichier metadata introuvable : {metadata_path}")
    raise SystemExit(1)

print(f"Métadonnées chargées pour {len(books_data)} ouvrages.")


# =========================
# Lire le CSV agrégé
# =========================

combined_path = os.path.join(SCRIPT_DIR, COMBINED_CSV)
if not os.path.exists(combined_path):
    print(f"CSV agrégé introuvable : {combined_path}")
    raise SystemExit(1)

distances_par_livre = defaultdict(list)
lignes_sans_metadata = 0
lignes_sans_date = 0

with open(combined_path, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f, delimiter=CSV_DELIMITER)

    # Nettoyer les en-têtes (espaces invisibles possibles)
    if reader.fieldnames:
        reader.fieldnames = [c.strip() for c in reader.fieldnames]

    # Vérifier colonnes obligatoires
    if BOOK_KEY_COLUMN not in (reader.fieldnames or []):
        print(f"Colonne '{BOOK_KEY_COLUMN}' absente du CSV : {combined_path}")
        print(f"Colonnes disponibles : {reader.fieldnames}")
        raise SystemExit(1)

    if EVENT_DATE_COLUMN not in (reader.fieldnames or []):
        print(f"Colonne '{EVENT_DATE_COLUMN}' absente du CSV : {combined_path}")
        print(f"Colonnes disponibles : {reader.fieldnames}")
        raise SystemExit(1)

    for row in reader:
        raw_book = row.get(BOOK_KEY_COLUMN)
        if not raw_book:
            lignes_sans_metadata += 1
            continue

        mapped_title = TITLE_TO_FILEKEY.get(raw_book, raw_book)
        book_key_norm = normalize_key(mapped_title)

        # 1) correspondance exacte
        book_info = books_data.get(book_key_norm)

        # 2) fallback : correspondance partielle
        if not book_info:
            for k, v in books_data.items():
                if book_key_norm and (book_key_norm in k or k in book_key_norm):
                    book_info = v
                    break

        if not book_info:
            lignes_sans_metadata += 1
            continue

        event_year = parse_event_date(row.get(EVENT_DATE_COLUMN))
        if event_year is None:
            lignes_sans_date += 1
            continue

        distance = book_info["date"] - event_year
        livre_label = f"{book_info['title']}\n({book_info['date']})"
        distances_par_livre[livre_label].append(distance)

print(f"Lignes ignorées (pas de metadata trouvée) : {lignes_sans_metadata}")
print(f"Lignes ignorées (date-stat inexploitable) : {lignes_sans_date}")


# =========================
# Plot + stats
# =========================

distances_finales = {k: v for k, v in distances_par_livre.items() if v}

if not distances_finales:
    print("Aucune donnée exploitable (vérifie 'Titre source' ↔ metadata et 'date-stat').")
    raise SystemExit(1)

print(f"Données trouvées pour {len(distances_finales)} ouvrages.")

plt.style.use("seaborn-v0_8")
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.size"] = 10

fig, ax = plt.subplots(figsize=(14, 8))

# ====================================================
# TRI CHRONOLOGIQUE DES OUVRAGES
# ====================================================

def extract_year_from_label(label):
    # label format : "Titre\n(1574)"
    m = re.search(r"\((\d{4})\)", label)
    return int(m.group(1)) if m else 9999

# tri par année croissante
labels = sorted(distances_finales.keys(), key=extract_year_from_label)

# données dans le même ordre
data = [distances_finales[l] for l in labels]

violin_parts = ax.violinplot(
    data,
    positions=range(len(labels)),
    showmeans=True,
    showmedians=True
)

# Couleurs
for pc in violin_parts["bodies"]:
    pc.set_facecolor("#8A2BE2")
    pc.set_alpha(0.7)

violin_parts["cmeans"].set_color("#2E8B57")
violin_parts["cmedians"].set_color("#FF6347")
violin_parts["cbars"].set_color("black")
violin_parts["cmins"].set_color("black")
violin_parts["cmaxes"].set_color("black")

ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha="right")
ax.set_ylabel("Distance temporelle (années)", fontsize=12, fontweight="bold")
ax.set_title(
    "Distribution des distances temporelles entre ouvrages et événements utilisés",
    fontsize=14, fontweight="bold", pad=20
)

fig.suptitle(
    "Lecture : largeur = densité d'événements à cette distance.\n"
    "Valeurs positives = événements antérieurs à la publication | Valeurs négatives = anachronismes",
    fontsize=11, y=0.02, ha="center", style="italic"
)

ax.axhline(y=0, color="red", linestyle="--", alpha=0.7, linewidth=2, label="Distance = 0")

ax.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)
ax.set_facecolor("#f8f9fa")

from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color="#2E8B57", lw=3, label="Moyenne"),
    Line2D([0], [0], color="#FF6347", lw=3, label="Médiane"),
    Line2D([0], [0], color="red", linestyle="--", alpha=0.7, label="Distance = 0"),
    plt.Rectangle((0, 0), 1, 1, facecolor="#8A2BE2", alpha=0.7, label="Distribution"),
]
ax.legend(handles=legend_elements, loc="upper right", frameon=True, shadow=True, fontsize=10)

plt.tight_layout()

output_file = os.path.join(SCRIPT_DIR, "distances_temporelles_violon.png")
plt.savefig(output_file, dpi=300, bbox_inches="tight")
print(f"\nDiagramme sauvegardé : {output_file}")

plt.show()

print("\n=== STATISTIQUES ===")
for label, distances in distances_finales.items():
    moyenne = float(np.mean(distances))
    mediane = float(np.median(distances))
    print(label)
    print(f"  - Moyenne : {moyenne:.1f} ans")
    print(f"  - Médiane : {mediane:.1f} ans")
    print(f"  - N       : {len(distances)}")
    print()