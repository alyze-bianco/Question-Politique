# Computational Analysis of Narrative Exempla in Protestant Monarchomach Writings

This repository contains the data-processing workflow, scripts, and analytical materials developed for a computational study of narrative *exempla* in sixteenth-century Protestant monarchomach writings.

The project investigates how political authors of the French Wars of Religion mobilised historical, biblical, legal, and mythological examples in order to construct political authority and argumentative proof. It focuses in particular on the *Question politique, s’il est licite aux subjects de capituler avec leur prince*, attributed to Jean de Coras, and compares it with a broader corpus of monarchomach texts.

## Research Context

The study is situated at the intersection of early modern intellectual history, rhetoric, textual scholarship, and digital humanities.

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

## Methodology

The workflow follows several stages:

1. **Data preparation**
   - Layout analysis of early modern printed sources.
   - OCR / HTR processing.
   - Manual correction of transcriptions.
   - Export of textual data from XML-ALTO to XML-TEI.

2. **Textual enrichment**
   - Semi-automatic normalisation of sixteenth-century French.
   - Use of `<orig>` and `<reg>` TEI tags to preserve both original and regularised forms.
   - Progressive enrichment of a lexical resource adapted to the corpus.

3. **Data extraction**
   - Extraction of relevant textual and rhetorical information using Python scripts.
   - Conversion of structured data into `.txt` and `.csv` formats.
   - Identification and verification of narrative *exempla*.

4. **Dating and classification**
   - Historical dating of events, figures, and references.
   - Use of historical reference data, including Wikidata where applicable.
   - Approximate dating of long periods using median dates.
   - Specific treatment of biblical references through a conventional chronological framework.

5. **Statistical analysis and visualisation**
   - Computation of temporal distance between the date of each text and the events mobilised as *exempla*.
   - Classification of references by historical period.
   - Visualisation using Python and Matplotlib.

## Historical Categories

The references are classified into the following analytical categories:

- Biblical Antiquity
- Classical Antiquity
- Early Middle Ages
- Late Middle Ages
- Contemporary period of the author
- Mythology

These categories are used as operational tools for comparison and visualisation. They are not intended to reproduce sixteenth-century historical consciousness exactly.

## Main Analytical Goals

This repository supports several research objectives:

- Measuring the temporal depth of *exempla* used in monarchomach writings.
- Comparing argumentative strategies across different authors and texts.
- Identifying whether certain texts rely more heavily on contemporary, classical, medieval, or biblical references.
- Testing whether the *Question politique* presents a distinctive argumentative profile.
- Building a reusable workflow for larger corpora of early modern political texts.

## Preliminary Results

The first results show two major temporal regimes in the corpus:

1. A use of the recent past, especially in texts concerned with immediate political experience.
2. A use of the distant past, especially Classical Antiquity and, in some cases, Biblical Antiquity.

The *Question politique* appears to occupy an intermediate position. It combines contemporary political references with learned historical and biblical examples. This hybrid profile may contribute to future attribution studies, provided that the corpus is further stabilised and normalised.

The analysis also suggests that monarchomach argumentation combines two modes of proof:

- a cumulative logic, based on the accumulation of historical precedents;
- an exemplary logic, in which specific cases are elevated as political models.

## Repository Structure

The final structure of the repository may follow this model:

```text
.
├── data/
│   ├── alto/              # XML-ALTO files
│   ├── tei/               # XML-TEI files
│   ├── txt/               # Plain-text versions
│   └── csv/               # Extracted and structured data
│
├── scripts/
│   ├── normalization/     # Scripts for semi-automatic normalisation
│   ├── extraction/        # Scripts for extracting exempla and metadata
│   └── analysis/          # Statistical analysis and visualisation scripts
│
├── notebooks/             # Exploratory analysis notebooks
├── figures/               # Generated graphs and visualisations
├── docs/                  # Documentation
├── README.md
└── LICENSE
