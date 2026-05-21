import re
from pathlib import Path
import pandas as pd

sources_dir = Path("reg_extraits")

mon_dictionnaire = {
    "Le Politique (1576)": "le_politique_1576",
    "La Gaule Françoise (1574)" : "gaule_francoise_1574",
    "Du droit des magistrats (1574)" : "droit_des_magistrats_1574",
    "De la puissance légitime (1581)" : "de_la_puissance_legitime_1581",
    "Question Politique (1569)" : "question_politique_1569",
    "Le Réveille-matin (1574)" : "le_reveille_matin_1574",
    "Discours politiques (1578)" : "discours_politiques_des_diverses_puissances_1578"
}

def normalize_text(s: str) -> str:
    """Normalise texte/citation pour réduire les faux négatifs."""
    s = "" if s is None else str(s)

    # caractères typographiques fréquents
    s = s.replace("\u00A0", " ")     # espace insécable
    s = s.replace("’", "'")
    s = s.replace("–", "-").replace("—", "-")
    s = s.replace("«", '"').replace("»", '"')

    # enlève les césures de fin de ligne: "peu-\nple" -> "peuple"
    # (même si le PDF/TXT a été généré avec des retours à la ligne)
    s = re.sub(r"(\w)-\s+(\w)", r"\1\2", s, flags=re.UNICODE)

    # compacte tous les espaces (retours ligne inclus)
    s = " ".join(s.split())

    return s

def clean_citation(citation: str) -> str:
    c = "" if citation is None else str(citation)

    # retire les guillemets englobants si présents
    c = c.strip()
    if len(c) >= 2 and ((c[0] == '"' and c[-1] == '"') or (c[0] == "'" and c[-1] == "'")):
        c = c[1:-1]

    # supprime les marqueurs entre crochets : [1], [5, 6], [12-13] etc.
    c = re.sub(r"\[\s*\d+(?:\s*[-,]\s*\d+)*\s*\]", "", c)

    return normalize_text(c)

def citation_presente(titre_source_fichier: str, citation: str):
    try:
        texte = (sources_dir / f"{titre_source_fichier}.txt").read_text(encoding="utf-8")
    except FileNotFoundError:
        return "source introuvable"

    texte_norm = normalize_text(texte)
    cit_norm = clean_citation(citation)

    if not cit_norm:
        return False

    # Si la citation est tronquée avec "..." (ou "…"), on utilise une regex "wildcard"
    if "..." in cit_norm or "…" in cit_norm:
        pattern = re.escape(cit_norm)
        pattern = pattern.replace(re.escape("..."), r".*?").replace(re.escape("…"), r".*?")
        return re.search(pattern, texte_norm, flags=re.DOTALL) is not None

    # Sinon recherche exacte normalisée
    return cit_norm in texte_norm

# Application
df = pd.read_csv("CSV/corpus.csv", delimiter=";")
df["citation_verifiee"] = df.apply(
    lambda row: citation_presente(mon_dictionnaire[row["Titre source"]], row[" Citations"]),
    axis=1
)
df.to_csv("corpus_verifie.csv", index=False)
