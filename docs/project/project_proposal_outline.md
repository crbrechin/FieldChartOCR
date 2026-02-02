# Project Proposal Outline: HexSight Chart Intelligence Platform

## Title Ideas
- HexSight: Color-Aware Extraction of Handwritten Charts and Tables
- HexSight Chart Intelligence (HexCI) Platform

## Abstract (Key Points)
- Motivation: handwritten technical notes and charts trap structured knowledge.
- Goal: build a modular pipeline that converts scanned notes into semantic outputs (Markdown/CSV/JSON).
- Approach: color-phase normalization, chart classification, element detection, OCR, semantic assembly.
- Impact: enables fast digitization, analytics, and Desmos-style visualization.

## 1. Introduction
- Problem statement: recovering structured data from multi-color handwritten charts, tables, and diagrams.
- Importance: accelerates documentation, supports accessibility, fuels downstream analytics/AI assistants.
- Context: current OCR handles text but fails on heterogeneous charts and color semantics.
- Contribution preview: unified, color-aware pipeline with modular sub-models, covering six chart families plus tables.

## 2. Related Work (Buckets to Discuss)
- **Chart Understanding Systems**: ChartOCR, ChartSense, Revision, DVQA.
- **Diagram Parsing & Table Recognition**: DiagramParseNet, ChartQA, table structure recognition (DeepDeSRT).
- **Handwriting OCR**: transformer-based handwriting recognizers, MathOCR, LaTeX translation.
- **Color Normalization & Multispectral Imaging**: methods for color constancy, UV imaging research.

## 3. Proposed Work
### 3.1 Data Sources
- Hand-drawn notebooks (provided sample set), future scans.
- Public chart datasets (ExcelChart400K, DVQA) for pretraining.
- Synthetic augmentations for mechanical drawings and network diagrams.

### 3.2 System Architecture
1. **Preprocessing & Color Normalization**  
   - Hex `#RRGGBBAA` conversion, color-phase normalization, future UV channel hooks.
2. **Chart Type Classifier**  
   - Multi-label classifier covering timesheets, network diagrams, bar graphs, scatterplots, mechanical drawings, LaTeX expressions.
3. **Element Identification Modules**  
   - Shared detection backbone with task-specific heads (axes, scales, data marks, trend lines, symbols, formulas).
   - Table structure detector producing cell meshes for CSV export.
4. **OCR Layer**  
   - Handwriting OCR with color tags, math-aware recognition for LaTeX, dimension text extractor for mechanical drawings.
5. **Semantic Assembly & Validation**  
   - Associate text with elements, enforce geometric consistency, perform rule-based checks.
6. **Output Writers**  
   - Markdown summary, dataset-specific CSV files, JSON semantic graph linking elements and colors.

### 3.3 Task Prioritization
- MVP: color normalization, chart classification, bar/line/scatter extraction, table-to-CSV.
- Phase 2: timesheets, network diagrams, mechanical drawings, LaTeX translator.
- Phase 3: logical gate transform layer, UV channel fusion.

## 4. Evaluation Plan
- **Effectiveness Metrics**  
  - Classification accuracy/F1 per chart type.  
  - Element detection precision/recall (bars, nodes, axes).  
  - OCR WER/CER with color agreement accuracy.  
  - Table reconstruction metrics (cell F1, structural F-score).  
  - Output fidelity vs. ground-truth CSV/JSON using Earth Mover’s Distance or normalized error.
- **Efficiency Metrics**  
  - Runtime per page, throughput (pages/minute), GPU/CPU utilization.  
  - Memory footprint for embedded deployment.
- **Experimental Setup**  
  - Stratified train/val/test splits per chart type.  
  - Baselines: ChartOCR, standard OCR+heuristics, table parsers (TabStructNet).  
  - Cross-validation on limited hand-drawn dataset; ablation on color normalization and semantic checks.

## 5. Timeline & Current Status
- **Week 1**: Collect dataset samples, finalize labeling schema, build annotation guidelines.
- **Week 2**: Implement preprocessing + color normalization prototype; run baseline OCR tests.
- **Week 3**: Train chart classifier; integrate bar/line modules; evaluate on held-out pages.
- **Week 4**: Add table parser and CSV exporter; start semantic assembly layer.
- **Week 5**: Extend to network diagrams & mechanical drawings; incorporate math OCR.
- **Week 6**: Full pipeline evaluation, error analysis, iterate on challenging cases.
- Current status: requirement analysis, architecture design, literature review (ChartOCR and related systems).

## 6. Risks & Mitigation
- **Limited Hand-Drawn Data**: augment via synthetic generation and active learning.  
- **Color Variability**: rely on normalization layer with calibration targets; incorporate UV roadmap.  
- **Model Complexity**: modular training schedule, shared backbone to manage compute.  
- **Table Ground Truth**: design annotation tools; start with semi-automatic alignments and manual QA.

## 7. Conclusion & Future Work
- Recap color-aware modular pipeline and expected benefits.  
- Outline future enhancements: logical gate transform layer, UV multispectral capture, interoperability with Desmos-like visualizer and CAD tools.

