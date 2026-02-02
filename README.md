# DTSA-5506 Project Repository

This repository contains coursework and project artifacts for DTSA-5506, organized into a
GitHub-friendly layout with a clean separation of source code, notebooks, data, assets,
and documentation.

## Repository structure

- `src/` - Source code and libraries.
- `notebooks/` - Jupyter notebooks (outputs stripped).
- `data/` - Small reference datasets used by notebooks and scripts.
- `assets/source/` - Source images and reference graphics.
- `assets/generated/` - Generated images and derived assets (ignored by git).
- `docs/` - Project documentation, papers, and reports.
- `outputs/` - Generated artifacts and tables (ignored by git).

## Quick start

1. Create and activate a Python environment.
2. Install dependencies needed for the notebooks or `src/` tools.
3. Open notebooks from `notebooks/` and run cells as needed.

## Notebooks

- Notebook outputs are stripped to keep the repo clean.
- Image paths in notebooks assume the notebook is run from `notebooks/`.
- Example data is under `data/` and images are under `assets/`.

## Data and assets

- Large image datasets are kept locally and are ignored by git:
  - `samples/`
  - `mileage_reports/`
  - `hand_drawn_notes/`
- Generated outputs should go to `outputs/` or `assets/generated/`.

## Documentation

See `docs/structure.md` for a detailed folder map and data handling notes.
