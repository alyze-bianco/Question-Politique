# Computational Analysis of Narrative *Exempla* in Protestant Monarchomach Writings

This repository contains the data-processing workflow, scripts, and analytical materials developed for a computational study of narrative *exempla* in sixteenth-century Protestant monarchomach writings.

The project investigates how political authors of the French Wars of Religion mobilised historical, biblical, legal, and mythological examples in order to construct political authority and argumentative proof. It focuses in particular on the *Question politique, s’il est licite aux subjects de capituler avec leur prince*, attributed to Jean de Coras, and compares it with a broader corpus of monarchomach texts.

## Research Context

The study is situated at the intersection of early modern intellectual history, rhetoric and digital humanities.

The main research question is:

> To what extent can computational analysis characterise the use of narrative *exempla* in Protestant monarchomach treatises and identify argumentative profiles specific to each text?

The project does not rely on large-scale corpus analysis. Instead, it uses computational methods to systematise the identification, classification, dating, and visualisation of *exempla* across a restricted but historically significant corpus.

## Corpus

The corpus is composed of seven monarchomach texts written between 1569 and 1581:

| Text | Author / Attribution | Date | Length |
|---|---:|---:|---:|
| *Question politique* | Jean de Coras | 1569 | 48 pages |
| *La Gaule Françoise* | François Hotman | 1574 | 227 pages |
| *Le Réveille-Matin des François* | Eusèbe Philadelphe Cosmopolite | 1574 | 389 pages |
| *Du droit des magistrats* | Théodore de Bèze | 1574 | 84 pages |
| *Le Politique* | Anonymous / NR | 1576 | 80 pages |
| *Discours des diverses puissances* | Anonymous / NR | 1578 | 147 pages |
| *De la puissance légitime du prince* | Stephanus Junius Brutus | 1581 | 271 pages |


## Main Analytical Goals

This repository supports several research objectives:

- Measuring the temporal depth of *exempla* used in monarchomach writings.
- Comparing argumentative strategies across different authors and texts.
- Identifying whether certain texts rely more heavily on contemporary, classical, medieval, or biblical references.
- Testing whether the *Question politique* presents a distinctive argumentative profile.
- Building a reusable workflow for larger corpora of early modern political texts.


## Repository Structure

The final structure of the repository may follow this model:

'''
Question-Politique/
├── Data/
│   ├── Alto/              # XML-ALTO files
│   ├── CSV/               # Extracted and structured data
│   ├── TEI/               # XML-TEI files
│   └── TXT/               # Plain-text versions
│
├── Figures/
│   ├── Statistiques_évènements_052026.png
│   └── distancestemporelles_052026.png
│
├── Scripts/
│   ├── Extractor.py
│   │   └── Extracts <reg> tags from XML-TEI files and exports them as TXT files.
│   │
│   ├── distance_temporelle_date_stat.py
│   │   └── Computes temporal distances between the date of each text and the date of the events cited.
│   │
│   ├── normalizator.py
│   │   └── Semi-automatically normalizes a sixteenth-century corpus into a semi-diplomatic transcription.
│   │
│   ├── renomination.py
│   │   └── Renames image files.
│   │
│   └── stat_periodes.py
│       └── Computes the periodization of the texts and the distribution of events by historical period.
│
├── .gitattributes
└── README.md
'''

## License
Unless otherwise indicated, all content in this repository is released under:

Creative Commons Attribution 4.0 International (CC BY 4.0)
👉 https://creativecommons.org/licenses/by/4.0/

## Citation
If you wish to cite this repository as a whole, please use:

Alyzé Bianco, Computational Analysis of Narrative Exempla in Protestant Monarchomach Writings , GitHub repository, 2025. CC BY 4.0.
Available at: https://github.com/alyze-bianco/Question-Politique


## Acknowledgments
This repository is maintained by Alyzé Bianco (FNS Scientific Collaborator, University of Geneva).
It is part of ongoing research on *La Question Politique* de Jean de Coras
