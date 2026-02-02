# FieldChartOCR: Extraction of Handwritten Charts and Tables

## Abstract
Handwritten charts and technical notes are rich with quantitative insight yet remain locked inside scanned pages. FieldChartOCR extends ChartOCR to converting hand-drawn charts and tables into structured datasets. The procedure goes through chart classification, element detection, and handwriting OCR, to information extraction. The focus is on delivering a practical tool that field technicians and researchers can rely on without exhaustive manual transcription.

## 1. Introduction
Digitizing handwritten technical notebooks is labour-intensive. Engineers, students, and analysts rely on annotations, sketches, and mixed layouts that resist automated extraction. Existing OCR tools, like ChartOCR, provide plain text at best; they ignore hand-drawn informatics in order to optimize accuracy. On the other hand, professionals (such as field technicians) must manually re-create charts in tools such as Excel, Desmos, or CAD systems—a significant barrier to iteration and collaboration.

The goal of FieldChartOCR is to build a unified pipeline that ingests handwritten graphs, tables, and mechanical annotations and produces structured artifacts suitable for analytics and visualization. By coupling deep learning with rule-based reasoning, I hope to generalize across chart families while maintaining transparency in intermediate outputs. Delivering this capability advances document understanding, accelerates knowledge sharing, and supports accessibility by providing machine-readable alternatives to complex figures.


## 2. Related Work
- **Chart Understanding Frameworks:** ChartOCR’s hybrid keypoint-and-rule architecture demonstrates the effectiveness of combining deep detection with domain logic. ChartSense and ReVision apply rule-based heuristics but struggle with diverse layouts. DVQA and FigureQA focus on question answering but assume neatly rendered charts.
- **Diagram & Table Recognition:** DiagramParseNet and other graph-parsing models detect nodes and edges in structured diagrams. DeepDeSRT and PubTabNet handle printed tables yet rely on sharp lines and consistent fonts, unlike the irregular strokes in hand-drawn notes.
- **Handwriting OCR & Math Recognition:** Transformer-based handwriting recognizers and MathOCR systems convert cursive and symbolic notation into LaTeX. They typically operate on grayscale inputs and overlook complex layouts.
- **Document Normalization & Imaging:** Research on illumination correction and phase-based representations inspires our preprocessing layer. Multispectral imaging studies inform our roadmap for future sensing modalities.

## 3. Proposed Work

### 3.1 Data Sources
- handwritten notebooks and diagrams.
- corresponding digital diagrams and comma separated list of data for training validation
- In order to avoid informational leaks, I will synthesize my datasets to cover varied topics of study.

### 3.2 System Architecture
1. **Preprocessing & Layout Normalization**  
   - Perform denoising, skew correction, grid suppression, and edge enhancement tailored to notebook paper.  
   - Standardize contrast and dynamic range to support downstream detectors.
   - **Note:** I may move to scanning the images if this part proves too onerous.
2. **Chart Type Classification**  
   - Lightweight CNN-transformer hybrid predicts dominant chart categories for each region.
    - The goal is to match the 3 charts recognized by ChartOCR: bar charts, line charts, and pie charts.  
   - Supports mixed-content pages by assigning probabilities per region.
3. **Element Identification & OCR**  
   - Shared detection backbone with heads for axes, scales, titles, data marks, and table structure.
4. **Semantic Assembly & Output**  
   - Associates text blocks with detected elements, enforces basic geometric constraints, and exports Markdown summaries plus CSV datasets.

### 3.3 Development Plan
- **Phase 1:** Build preprocessing pipeline, layout normalization, and table-to-CSV baseline.  
- **Phase 2:** Train chart classifier and core element detectors; integrate handwriting OCR.  
- **Phase 3:** Finalize semantic assembly, polish outputs, and iterate on error analysis.

## 4. Evaluation Plan
- **Effectiveness Metrics**  
  - Chart classification macro-F1 across core categories (bar, line, scatter, tables).  
  - Element detection precision/recall for axes, titles, and data marks.  
  - OCR character error rate (CER) and table reconstruction F1.  
- **Efficiency Metrics**  
  - End-to-end runtime per page and memory footprint.  
- **Experimental Setup**  
  - Stratified train/validation/test split by chart type and handwriting style.  
  - Baselines: ChartOCR, generic OCR plus heuristic extraction, and manual transcription samples.  
  - Ablations on preprocessing and semantic assembly.

## 5. Timeline & Milestones
| Week | Milestone |
| --- | --- |
| 1 | Finalize annotation schema, label initial dataset, implement normalization prototype. |
| 2 | Integrate baseline handwriting OCR and chart classifier; evaluate on sample pages. |
| 3 | Deploy element detectors and table recognizer; stand up Markdown/CSV writers. |
| 4 | Iterate on semantic assembly, run core evaluations, and prepare presentation materials. |

Current progress: completed literature review, defined architecture, and collected representative notebook scans.

## 6. Risks and Mitigation
- **Limited Hand-Drawn Training Data**  
  - Mitigation: remove the information extraction steps and keep only the classification.
- **Complex Page Layouts**  
  - Mitigation: flag difficult cases for human review.
- **Lighting Noise**  
  - Mitigation: use normalization targets, augment brightness/contrast, and monitor detector confidence.

## 7. Conclusion and Future Work
FieldChartOCR delivers a modular approach to handwritten chart understanding that bridges the gap between raw scans and analytic-ready datasets. The simplified plan concentrates on a single, reliable pipeline that extracts layout structure and exports Markdown and CSV artifacts. Future work will explore richer diagram types and collaborative review tooling once the MVP demonstrates consistent performance.

## References
1. Xiao Liu et al. “ChartOCR: Data Extraction from Charts Images via a Deep Hybrid Framework,” 2020.  
2. Manolis Savva et al. “Revision: Automated Classification, Analysis, and Redesign of Chart Images,” UIST 2011.  
3. Daekyoung Jung et al. “ChartSense: Interactive Data Extraction from Chart Images,” CHI 2017.  
4. Priyanka Mondal et al. “DeepDeSRT: Deep Learning for Table Structure Recognition,” ICDAR 2019.  
5. Cheng-Zhi Anna Huang et al. “Diagram Understanding Methods: A Survey,” 2021.  
6. Zhe Li et al. “Handwritten Mathematical Expression Recognition via Transformer,” 2022.  
7. Nickolas Gatos et al. “Adaptive Document Image Binarization,” ICPR 2004.