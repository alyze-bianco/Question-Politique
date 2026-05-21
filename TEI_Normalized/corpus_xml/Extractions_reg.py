from pathlib import Path
import re
import xml.etree.ElementTree as ET

INPUT_DIR = Path("corpus_xml")      # dossier des .xml
OUTPUT_DIR = Path("reg_extraits")   # dossier de sortie
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}

def normalize_whitespace(s: str) -> str:
    # évite les espaces/sauts de ligne multiples dus au balisage
    return re.sub(r"\s+", " ", s).strip()

for xml_path in sorted(INPUT_DIR.glob("*.xml")):
    out_path = OUTPUT_DIR / (xml_path.stem + ".txt")

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Option A (souvent préférable) : seulement dans <text>
        regs = root.findall(".//tei:text//tei:reg", TEI_NS)

        # Option B : partout (y compris teiHeader/sourceDoc)
        # regs = root.findall(".//tei:reg", TEI_NS)

        with out_path.open("w", encoding="utf-8") as out:
            for reg in regs:
                # récupère texte + texte des sous-éléments + tails, dans l’ordre
                content = "".join(reg.itertext())
                content = normalize_whitespace(content)
                if content:
                    out.write(content + "\n")

        print(f"OK: {xml_path.name} -> {out_path.name}")

    except ET.ParseError as e:
        print(f"XML mal formé: {xml_path.name} ({e})")
    except Exception as e:
        print(f"Erreur: {xml_path.name} ({e})")
