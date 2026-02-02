# Repository structure and data notes

This document explains the folder layout and how to handle data and assets.

## Folder map

- `src/` - Core source code and project modules.
  - `src/FieldChartOCR/` contains the main chart OCR implementation.
  - `src/scripts/` contains utility scripts.
- `notebooks/` - Jupyter notebooks with outputs stripped.
- `data/` - Small datasets used by notebooks and scripts.
  - `data/bar_charts/` holds CSV/JSON samples for bar chart parsing.
- `assets/source/` - Source/reference images and figures.
  - `assets/source/fieldchartocr/` holds source images used by FieldChartOCR.
- `assets/generated/` - Generated figures and derived images.
  - `assets/generated/output_files/` holds generated figures from notebooks.
  - `assets/generated/fieldchartocr/` holds temporary images from scripts.
- `outputs/` - Generated artifacts such as tables and logs.
  - `outputs/tables/` holds generated CSVs.
  - `outputs/fieldchartocr/` holds runtime logs and DBs.
- `docs/` - Documentation, references, and project materials.
  - `docs/references/` contains research papers and citations.
  - `docs/notebook_exports/` contains notebook exports (PDF/HTML).
  - `docs/project/` contains project proposals, reports, and slides.
  - `docs/misc/` contains unrelated or one-off documents.

## Data and asset handling

- Source assets should go under `assets/source/`.
- Generated images should go under `assets/generated/`.
- Large local datasets are excluded from git and kept locally:
  - `samples/`
  - `mileage_reports/`
  - `hand_drawn_notes/`

## Notebook paths

Notebooks assume they are run from the `notebooks/` directory. Use relative paths like:

- `../data/...`
- `../assets/source/...`
- `../assets/generated/...`
