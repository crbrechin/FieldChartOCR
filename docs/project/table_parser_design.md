# Hand-Drawn Table Parsing Design Notes

## 1. Sample Inventory & Observations
- **Mechanical dimension pages** feature sparse tables with measurement annotations, dotted leader lines, and mixed units. Borders are incomplete and often implied by grid paper rather than explicit strokes.
- **Tensor/vector lecture notes** include multi-color matrices and aligned equations; cells are separated by handwritten braces or underline marks instead of full boxes.
- **Timesheet-style pages** list columns of dates and metrics with colored highlights indicating teams or statuses.
- **Alphabet & symbol practice sheets** contain dense grids with monotone pencil strokes; grid lines from the notebook are darker than the ink.
- **Mixed-content spreads** combine tables with graphs, diagrams, and narrative text; tables may appear rotated or partially occluded by drawings.

### Implications
- Expect **broken or implied cell boundaries**; the parser must leverage grid paper structure and text alignment cues.
- **Color encoding is meaningful** (e.g., green vs. blue headings). Preserve per-cell color in `#RRGGBBAA` format to keep model identities.
- Background grid lines introduce noise; preprocessing should attenuate background frequency patterns without erasing pale ink.

## 2. Target CSV Schemas
| Use Case | CSV Columns | Notes |
| --- | --- | --- |
| Rectangular tables | `row_index`, `column_index`, `text`, `hex_rgba`, `confidence`, `row_span`, `col_span` | Supports merged cells by repeating metadata; `text` may contain `\n` for multi-line entries. |
| Timesheet / schedule | `task_id`, `task_label`, `start`, `end`, `duration`, `color_id`, `notes` | Derived from bar-like cells aligned along timeline axis. |
| Mechanical dimensions | `feature_id`, `feature_type`, `value`, `unit`, `tolerance`, `reference`, `hex_rgba` | Integrates symbol detection (Ø, ±) and dimension arrows. |
| Matrix / LaTeX tables | `row_index`, `column_index`, `latex_expr`, `hex_rgba` | Pair with Markdown/LaTeX rendering in final report. |

Shared conventions:
- `hex_rgba` stores normalized color from the color-phase module; transparent highlights use alpha `< FF`.
- `confidence` is the OCR probability for text; absent text uses empty string with low confidence.
- Output folder naming: `page_<id>_table_<k>.csv`; metadata stored in accompanying JSON (see Section 5).

## 3. Color Considerations
- Run the **color-phase normalization layer** before structural detection to convert captured RGB values into calibrated hex codes resistant to lighting variations.
- Maintain both **foreground stroke color** and **background highlight color** by sampling along the text baseline and surrounding area.
- For highlighter overlays, compute a per-cell `overlay_hex` and preserve the stroke `text_hex` separately to avoid averaging colors.
- Provide hooks for future **UV channel** fusion (store as `uv_phase` per cell inside JSON sidecar).

## 4. Model Stack for Table Structure Recognition
1. **Line & Junction Detector**  
   - Hybrid approach: differentiable Hough transform for long strokes + Mask2Former segmentation to capture faint or curved boundaries.  
   - Classify junctions (`L`, `T`, `X`) using a lightweight CNN on cropped regions; outputs feed graph construction.
2. **Cell Region Proposal**  
   - Generate candidate polygons by intersecting detected lines with segmentation masks.  
   - For missing borders, leverage text baselines and column alignment via a transformer-based **layout reasoner** that predicts vertical/horizontal separators.
3. **Text & Symbol Extraction**  
   - Apply CRAFT/ViT text detector to each candidate cell; run color-aware handwriting OCR (transformer decoder with color embeddings).  
   - Symbol detector (YOLOv8-tiny or DETR head) identifies checkmarks, dimension symbols, braces, and bullets.
4. **Table Graph Assembly**  
   - Construct a lattice graph where nodes represent cell polygons and edges encode adjacency.  
   - Run constraint solver (ILP or dynamic programming) to enforce rectangular structure, detect merged spans, and align with notebook grid derived from frequency analysis.

Training strategy:
- Label ~200 table instances with polygons, junction types, and text transcriptions.  
- Augment with synthetic hand-drawn tables generated via stroke simulation (varying pen pressure, jitter, color).  
- Fine-tune using multi-task loss combining segmentation, junction classification, and span detection.

## 5. CSV Writer & Validation Plan
### Conversion Pipeline
1. Sort cells by top-left coordinates; assign `row_index` and `column_index` using lattice graph ordering.
2. Propagate merged spans: for each cell spanning `r` rows or `c` columns, set `row_span`/`col_span` and leave covered cells empty or mark as `MERGED`.
3. Extract text (or LaTeX) alongside `hex_rgba`, OCR `confidence`, and any detected symbol tags.
4. Write CSV using UTF-8; escape newlines with quoted fields.  
5. Persist semantic metadata in `page_<id>_table_<k>.json` (structure definition, color overlays, UV placeholders, extraction version hash).

### Validation & QA
- **Structural Checks**: ensure each row has equal column count after span expansion; verify no overlapping polygons remain; confirm indices are monotonic.
- **Color Consistency**: compare `hex_rgba` against legend/label colors using ΔE thresholds; flag mismatches for review.
- **Numeric Consistency**: for tables containing quantities, run regex-based numeric extraction and check against expected bounds (e.g., tolerances, monotonically increasing time).
- **Confidence Thresholding**: mark cells with OCR confidence < 0.75 for manual validation; include flags in JSON.
- **Regression Tests**: maintain a benchmark suite of annotated tables; compute structural F1 and cell content accuracy after each model update.

### Edge Cases
- Wavy or torn page edges → apply perspective correction before parsing.
- Overlapping sketches -> segmentation masks isolate table region; if overlap persists, record occluded cells with `status="occluded"`.
- Rotated tables -> orientation classifier triggers rotation to canonical alignment prior to structure detection.
- Multi-table pages -> region clustering ensures each table receives a separate CSV + JSON pair.

## 6. Deliverables & Next Steps
- Build annotation guidelines for polygons, junctions, and merged cells using Label Studio.  
- Prototype color-phase normalization on sample scans; collect statistics on `hex_rgba` distribution per instrument color.  
- Implement baseline structural parser (line detection + heuristic grid) as a stepping stone before full transformer-based layout reasoning.

