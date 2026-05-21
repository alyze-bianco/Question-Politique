# Ce script permet d'extraire le texte des balises <reg> normalisées dans les fichiers XML du corpus, 
# en excluant celles qui sont dans des zones spécifiques (comme les titres, les marges, etc.). 
# Il genère un fichier texte pour chaque fichier XML traité, contenant les extraits de texte extraits des balises <reg>.

from pathlib import Path
import xml.etree.ElementTree as ET
import re

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "corpus_xml"
OUTPUT_DIR = BASE_DIR / "reg_extraits"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}

EXCLUDED_TYPES = {
    "RunningTitleZone",
    "QuireMarksZone",
    "NumberingZone",
    "MarginTextZone-Notes",
    "MarginTextZone-ManuscriptAddendum",
    "GraphicZone",
    "StampZone",
    "MarginTextZone",
    "MarginTextZone:handwrittenAddition",
    "DigitizationArtefactZone",
}

# ✅ Pour définir le fichier cible plutot qu'un dossier
TARGET_FILE = "le_reveille_matin_1574"  # <-- mettre le nom exact du fichier à traiter, ou laisser None pour tout traiter

def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def has_excluded_type_ancestor(elem, parent_map):
    parent = parent_map.get(elem)
    while parent is not None:
        t = parent.get("type")
        if t in EXCLUDED_TYPES:
            return True
        parent = parent_map.get(parent)
    return False

for xml_path in sorted(INPUT_DIR.glob("*.xml")):
    # ✅ Ne traiter que le fichier cible si TARGET_FILE est défini
    if TARGET_FILE is not None and xml_path.name != TARGET_FILE and xml_path.stem != TARGET_FILE:
        continue

    out_path = OUTPUT_DIR / (xml_path.stem + ".txt")

    tree = ET.parse(xml_path)
    root = tree.getroot()

    parent_map = {child: parent for parent in root.iter() for child in parent}

    regs = root.findall(".//tei:text//tei:reg", TEI_NS)

    kept = 0
    excluded = 0

    with out_path.open("w", encoding="utf-8") as out:
        for reg in regs:
            if has_excluded_type_ancestor(reg, parent_map):
                excluded += 1
                continue

            content = "".join(reg.itertext())
            content = normalize_whitespace(content)

            if content:
                out.write(content + "\n")
                kept += 1

    print(f"{xml_path.name}: {kept} extraits, {excluded} exclus")
