# ChartOCR: Data Extraction from Chart Images via a Deep Hybrid Framework

*Contribution during internship at Microsoft.*

## Abstract
Chart images are commonly used for data visualization. Automatically reading the underlying values is a key step toward comprehensive chart understanding, yet the wide variation in chart styles makes purely rule-based extraction brittle. At the same time, end-to-end deep learning approaches often overfit to specific chart types and provide limited control over intermediate representations. We present **ChartOCR**, a unified hybrid framework that combines deep learning with adaptable rules to extract data from a broad spectrum of charts. The method detects key points that define chart components, applies lightweight type-specific rules, and converts the result into structured tables. Experiments on public benchmarks and our newly introduced ExcelChart400K dataset demonstrate state-of-the-art accuracy and strong generalization. Code and data are available at [https://github.com/soap117/DeepRule](https://github.com/soap117/DeepRule).

## 1. Introduction
Chart images appear frequently in news articles, web pages, corporate reports, and scientific publications. Automatically recovering the data encoded in these graphics enables downstream applications such as document understanding, financial risk assessment, and accessibility tools for visually impaired readers. Unfortunately, when a chart is rendered as an image the original numerical table is lost.

![Figure 1: Example of data extraction from a chart image](chartocr_data_extraction_from_charts_images_via_a_deep_hybrid_framework-figure_1.png)

*Figure 1. Example of data extraction from a chart image.*

| Series   | Category 0 | Category 1 | Category 2 | Category 3 | Category 4 |
| ---      | ---:       | ---:       | ---:       | ---:       | ---:       |
| Series 0 | 40.58      | 41.55      | 41.56      | 42.34      | 42.35      |
| Series 1 | 22.66      | 22.67      | 24.66      | 24.68      | 26.43      |
| Series 2 | 15.02      | 15.05      | 15.88      | 16.85      | 17.66      |

Recent work on chart question answering also benefits from accurate data extraction. Earlier approaches rely heavily on manually crafted heuristics and thus struggle with the diversity of chart designs. Pure deep-learning solutions improve accuracy for limited chart families but lack interpretability and do not generalize to new chart types without retraining.

We address these limitations with a framework that frames chart component detection as a keypoint localization problem. ChartOCR first predicts chart type and semantic keypoints using a shared network, then applies type-aware rules to reconstruct bars, slices, or line segments before converting them into a structured table. The contributions of this work are:

- A deep hybrid pipeline that unifies learning-based detection with transparent rule-based reconstruction across bar, pie, and line charts.
- New evaluation metrics tailored to each chart family.
- ExcelChart400K, a large-scale dataset of annotated Excel charts to support deep model training.

## 2. Related Work

### 2.1 Rule-Based Methods
Feature-driven techniques detect chart elements via handcrafted cues such as color continuity and edge geometry. Candidate components are filtered through manually designed rules, which yields good performance on charts with consistent layouts but poor adaptability to varied orientations, stacked configurations, or atypical styles. Systems like ChartSense incorporate user feedback to mitigate errors at the expense of additional interaction.

### 2.2 Deep Neural Networks
Deep object detectors have been adapted to chart analysis by treating each bar or slice as an object, while recurrent networks model ordered data sequences. Although these methods improve accuracy and runtime, they remain specialized to the chart types seen during training. They also provide limited access to intermediate representations such as data ranges or plot areas.

### 2.3 Keypoint-Based Object Detection
Keypoint detectors have been successful in pose estimation, face alignment, and general object detection. Rather than predicting whole bounding boxes, they locate semantically meaningful points from which the object can be reconstructed. Charts share strong structural patterns, making keypoint-based extraction especially appealing. After detecting keypoints, chart-specific rules can assemble complete components.

## 3. Our Method
The ChartOCR pipeline comprises three modules (Figure 2):
- (i) common information extraction,
- (ii) data range estimation, and
- (iii) type-specific object reconstruction.

The first module predicts chart type and keypoints shared across chart families. The second infers the numerical data range for charts with axes. The third applies type-dependent grouping rules to recover full chart elements and converts them into a structured table.

![Figure 2: Overview of the ChartOCR framework](chartocr_data_extraction_from_charts_images_via_a_deep_hybrid_framework-figure_2.png)

*Figure 2. ChartOCR framework outline including common information extraction, data range extraction, and type-specific chart object detection.*

### 3.1 Common Information Extraction

#### Keypoint Detection
A modified CornerNet with a 104-layer Hourglass backbone produces pixel-level heatmaps for semantic keypoints. Depending on chart type, the model learns:

![Figure 3: Common information extraction network](chartocr_data_extraction_from_charts_images_via_a_deep_hybrid_framework-figure_3.png)

*Figure 3. Network architecture for joint keypoint detection and chart type classification.*

- Bar charts: top-left and bottom-right corners of individual bars.
- Line charts: pivot points along each line.
- Pie charts: chart center points and arc intersection points.

Corner pooling enlarges the receptive field to capture horizontal and vertical context. The network outputs a three-channel probability map (top-left, bottom-right, background). Training minimizes a combination of probability-map loss and smooth L1 loss for precise coordinates.

#### Chart Type Classification
An auxiliary convolutional branch reduces the feature map to a compact representation that feeds into fully connected layers with softmax activation. The cross-entropy objective

$$
\mathcal{L}_{\text{CE}}(y, p) = -\frac{1}{N} \sum_{i=1}^N \sum_{c=1}^C y_{ic} \log p_{ic}
$$

optimizes chart type recognition jointly with keypoint detection.

### 3.2 Data Range Extraction
A Microsoft OCR service extracts textual labels from the chart, including titles, legends, and axis annotations. For bar and line charts, we assume the y-axis labels lie to the left of the plot area. Detecting the plot area’s bounding box enables filtering OCR results to isolate axis values. The following procedure computes the numerical range:

```
Algorithm 1: Data Range Estimation
Require: plot bounds (top, left, bottom), OCR results R
Ensure: y_scale, y_min, y_max
1: r_max ← nearest numeric OCR token to (left, bottom) with x < left − 4
2: r_min ← nearest numeric OCR token to (left, top) with x < left − 4
3: y_scale ← (r_max.value − r_min.value) / (r_min.top − r_max.top)
4: y_min ← r_min.value − y_scale * (bottom − (r_min.top + r_min.bottom)/2)
5: y_max ← r_max.value + y_scale * ((r_max.top + r_max.bottom)/2 − top)
```

Pie charts omit this step because their sector values sum to 100% by definition.

### 3.3 Type-Specific Chart Object Detection

#### Bar Charts
Thresholded heatmaps yield candidate top-left and bottom-right corners. Each top-left point is paired with its closest bottom-right point via a weighted distance metric:

$$
\text{dist}(p_{tl}, p_{br}) = \gamma\,\text{dist}_x(p_{tl}, p_{br}) + \nu\,\text{dist}_y(p_{tl}, p_{br}),
$$

where $\gamma > \nu$ for vertical bars and $\nu > \gamma$ for horizontal bars. The resulting bounding boxes define bar extents.

#### Pie Charts
The corner pooling layer is replaced with center pooling to aggregate radial context. After thresholding, each sector is reconstructed by pairing a center point with consecutive arc points. Tight pies have a single center; exploded pies may contain multiple centers, so we estimate a common radius and verify candidate arc assignments within a tolerance.

```
Algorithm 2: Sector Combining
Require: centers {p_c}, arc points {p_a}, radius estimate r*, tolerance τ
Ensure: sectors represented by (p_c, p_a_start, p_a_end)
1: if |{p_c}| = 1 then
2:     sort {p_a} clockwise and emit adjacent pairs with the single center
3: else
4:     for each center p_c and arc point p_a
5:         find clockwise neighbor p_a*
6:         if |‖p_c − p_a‖ − r*| ≤ τ and |‖p_c − p_a*‖ − r*| ≤ τ
7:             emit sector (p_c, p_a, p_a*)
```

#### Line Charts
To group keypoints into lines, an embedding head encourages same-line points to cluster in feature space:

$$
\bar{e}_k = \frac{1}{N_k} \sum_i e_i^{(k)}, \qquad
\mathcal{L}_{\text{pull}} = \frac{1}{K} \sum_k \frac{1}{N_k} \sum_i \| e_i^{(k)} - \bar{e}_k \|^2,
$$

$$
\mathcal{L}_{\text{push}} = \frac{1}{K(K-1)} \sum_{i} \sum_{j>i} \max\!\left(1 - \| \bar{e}_i - \bar{e}_j \|, 0\right),
$$

$$
\mathcal{L}_{\text{embed}} = \mathcal{L}_{\text{pull}} + \mathcal{L}_{\text{push}}.
$$

The final loss is $\mathcal{L}_{\text{point}}' = \mathcal{L}_{\text{point}} + \lambda \mathcal{L}_{\text{embed}}$ with $\lambda = 0.1$. A union-find clustering algorithm associates points according to embedding similarity. Intersection points that belong to multiple lines are resolved by a QUERY network that samples along the candidate line segment and classifies whether the intersection should join the line.

## 4. Dataset
- **FQA**: 100 synthetic images covering bar, pie, and line charts with limited stylistic diversity.
- **WebData**: 100 web-crawled charts exhibiting broader style variation.
- **ExcelChart400K**: 386,966 Excel chart images collected via public spreadsheets. Charts are anonymized by replacing textual labels with random strings while preserving structure. Annotations include component bounding boxes and numerical values.

![Figure 4: Example chart images from ExcelChart400K](chartocr_data_extraction_from_charts_images_via_a_deep_hybrid_framework-figure_4.png)

*Figure 4. Representative samples from ExcelChart400K with annotated chart components.*

| Type | Train | Validation | Test |
| --- | ---: | ---: | ---: |
| Bar  | 173,249 | 6,935 | 6,970 |
| Line | 116,745 | 3,073 | 3,072 |
| Pie  | 73,075  | 1,924 | 1,923 |

## 5. Training Details
All chart types share the 104-layer Hourglass backbone. We train with Adam, learning rate $2.5 \times 10^{-4}$ and reduce it to $2.5 \times 10^{-5}$ for the final 5,000 batches. The batch size is 27, and focal loss parameters follow $\alpha = 2$, $\beta = 4$. Soft-NMS merges overlapping keypoint detections. Experiments run on four Tesla P100 GPUs with early stopping based on the ExcelChart400K validation split.

## 6. Evaluation Metrics
Existing metrics from general object detection or retrieval overlook chart-specific semantics. We design tailored metrics for each chart family.

### 6.1 Bar Chart Score
Let $p = [x_p, y_p, w_p, h_p]$ denote a predicted bar and $g = [x_g, y_g, w_g, h_g]$ a ground-truth bar. Define the distance

$$
D(p, g) = \min\!\left(1,\; \frac{|x_p - x_g|}{w_g} + \frac{|y_p - y_g|}{h_g} + \frac{|h_p - h_g|}{h_g}\right).
$$

Construct a cost matrix $C$ between all predictions and ground-truth bars, solve a Hungarian assignment to minimize total cost, and compute

$$
\text{score} = 1 - \frac{\text{cost}}{K},
$$

where $K = \max(N, M)$ and $N$, $M$ are the counts of predicted and ground-truth bars.

### 6.2 Line Chart Score
Predicted points $P = \{(x_i, y_i)\}_{i=1}^N$ and ground-truth points $G = \{(u_j, v_j)\}_{j=1}^M$ are compared via linear interpolation:

$$
\text{Err}(v_j, u_j, P) = \min\!\left(1, \left|\frac{v_j - I(P, u_j)}{v_j}\right|\right),
$$

where $I(P, u_j)$ interpolates $P$ at abscissa $u_j$. The weighting term

$$
\text{Intv}(j, G) =
\begin{cases}
\frac{u_{2} - u_{1}}{2}, & j = 1,\\[4pt]
\frac{u_{M} - u_{M-1}}{2}, & j = M,\\[4pt]
\frac{u_{j+1} - u_{j-1}}{2}, & \text{otherwise}
\end{cases}
$$

reflects spacing along the curve. Precision and recall share the same formulation:

$$
\text{Rec}(P, G) = \frac{\sum_{j=1}^M \left(1 - \text{Err}(v_j, u_j, P)\right) \text{Intv}(j, G)}{u_M - u_1},
$$

and $\text{Prec}(P, G) = \text{Rec}(G, P)$. The final F1 score is

$$
F_1 = \frac{2 \cdot \text{Prec} \cdot \text{Rec}}{\text{Prec} + \text{Rec}}.
$$

If multiple lines exist, the metric enumerates assignments between predicted and ground-truth lines to maximize the score.

### 6.3 Pie Chart Score
Pie charts require matching both sector magnitudes and ordering. Given predicted clockwise sequence $P = [x_1, \dots, x_N]$ and ground-truth $G = [y_1, \dots, y_M]$, dynamic programming computes

$$
\text{score}(i, j) = \max\Big(
\text{score}(i-1, j),
\text{score}(i, j-1),
\text{score}(i-1, j-1) + 1 - \left|\frac{x_i - y_j}{y_j}\right|
\Big),
$$

with $\text{score}(i, 0) = \text{score}(0, j) = 0$ and final value $\text{score}(N, M)/M$.

## 7. Experiments

### 7.1 Baselines
We compare ChartOCR against:

- **Revision**: a rule-based system covering bar and pie charts.
- **Vis**: a deep-learning pipeline with rule-based post-processing.
- **ResNet + Faster R-CNN**: enhanced detector for bars.
- **ResNet + Rotation RNN**: recurrent model for pie data extraction.
- **ResNet + RNN**: fully end-to-end approach that directly outputs sorted values.
- **ThinkCell**: a commercial bar-chart extraction tool accessed via GUI.

### 7.2 Quantitative Analysis
ChartOCR achieves the highest scores across all three chart families on ExcelChart400K:

| Method | Bar | Pie | Line |
| --- | ---: | ---: | ---: |
| ChartOCR | 0.919 | 0.918 | 0.962 |
| ChartOCR + GT Keypoints | 0.989 | 0.996 | 0.991 |
| ResNet + Faster R-CNN | 0.802 | — | — |
| Revision | 0.582 | 0.838 | — |
| ResNet + Rotation RNN | — | 0.797 | — |
| ResNet + RNN | 0.000 | 0.411 | 0.644 |

Replacing predicted keypoints with ground-truth annotations reveals the reliability of the rule-based reconstruction. Mean error rates on public datasets further highlight the gains:

| Dataset | Method | Bar ↓ | Pie ↓ | Line ↓ |
| --- | --- | ---: | ---: | ---: |
| FQA | ChartOCR + GT OCR | 0.093 | 0.038 | 0.496 |
|  | ChartOCR | 0.185 | 0.038 | 0.484 |
|  | Vis | 0.330 | 1.010 | 2.580 |
|  | Revision | 0.500 | 0.120 | — |
| WebData | ChartOCR | 0.285 | 0.439 | 0.740 |
|  | Vis | 0.450 | 0.810 | 2.070 |
|  | Revision | 2.230 | 0.570 | — |

### 7.3 Qualitative Analysis
ChartOCR remains robust across stacked, clustered, and tightly packed bar charts, whereas rule-based systems struggle with occlusion and background clutter (Figure 5). On pie charts with unusual colors or detached sectors, ChartOCR continues to segment slices accurately (Figures 6 and 7). For line charts, simple trajectories are captured well; complex multi-line intersections remain challenging due to QUERY network limitations (Figure 8).

![Figure 5: Comparison of methods on bar charts](chartocr_data_extraction_from_charts_images_via_a_deep_hybrid_framework-figure_5.png)

*Figure 5. Visual comparison between Revision, ThinkCell, ResNet+Faster-RCNN, and ChartOCR on diverse bar charts.*

![Figure 6: Example pie chart predictions](chartocr_data_extraction_from_charts_images_via_a_deep_hybrid_framework-figure_6.png)

*Figure 6. Comparison of numeric predictions on a pie chart for ChartOCR and baselines.*

![Figure 7: Pie chart with detached sectors](chartocr_data_extraction_from_charts_images_via_a_deep_hybrid_framework-figure_7.png)

*Figure 7. ChartOCR maintains accuracy on pie charts featuring detached sectors.*

![Figure 8: Line chart detection results](chartocr_data_extraction_from_charts_images_via_a_deep_hybrid_framework-figure_8.png)

*Figure 8. Easy and challenging line chart cases processed by ChartOCR.*

### 7.4 Efficiency
Average runtime (seconds per image):

| Method | Bar | Pie | Line |
| --- | ---: | ---: | ---: |
| ChartOCR | 0.206 | 0.193 | 0.507 |
| ResNet + Faster R-CNN | 0.120 | — | — |
| Revision | 20.032 | 5.423 | — |
| ResNet + Rotation RNN | — | 0.421 | — |

Line charts require additional processing for QUERY inference, doubling runtime relative to other chart types. Sharing parameters between keypoint and QUERY networks could further reduce latency.

## 8. Conclusion
ChartOCR combines deep keypoint detection with flexible rule-based reconstruction to recover data from diverse chart images. The framework generalizes across bar, line, and pie charts, provides interpretable intermediate outputs, and leverages the large ExcelChart400K dataset for training. Future work includes extending the approach to additional chart types and reducing runtime for complex line charts.

## References
1. Rabah A. Al-Zaidy, Sagnik Ray Choudhury, and C. Lee Giles. “Automatic summary generation for scientific data charts.” *Workshops at the 30th AAAI Conference*, 2016.  
2. Rabah A. Al-Zaidy and C. Lee Giles. “A machine learning approach for semantic structuring of scientific charts in scholarly documents.” *29th IAAI Conference*, 2017.  
3. Jihen Amara, Pawandeep Kaur, Michael Owonibi, and Bassem Bouaziz. “Convolutional neural network based chart image classification.” 2017.  
4. Abhijit Balaji, Thuvaarakkesh Ramanathan, and Venkateshwarlu Sonathi. “Chart-text: A fully automated chart image descriptor.” *arXiv:1812.10636*, 2018.  
5. Ritwick Chaudhry, Sumit Shekhar, Utkarsh Gupta, Pranav Maneriker, Prann Bansal, and Ajay Joshi. “Leaf-QA: Locate, encode & attend for figure question answering.” *arXiv:1907.12861*, 2019.  
6. Jinho Choi, Sanghun Jung, Deok Gun Park, Jaegul Choo, and Niklas Elmqvist. “Visualizing for the non-visual: Enabling the visually impaired to use visualization.” *Computer Graphics Forum*, 38:249–260, 2019.  
7. Kaiwen Duan, Song Bai, Lingxi Xie, Honggang Qi, Qingming Huang, and Qi Tian. “CenterNet: Keypoint triplets for object detection.” *arXiv:1904.08189*, 2019.  
8. Jinglun Gao, Zhou Yin, and K. E. Barner. “VIEW: Visual information extraction widget for improving chart images accessibility.” *IEEE International Conference on Image Processing*, 2013.  
9. Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. “Deep residual learning for image recognition.” *CVPR*, 2016.  
10. Weihua Huang and Chew Lim Tan. “A system for understanding imaged infographics and its applications.” *ACM Symposium on Document Engineering*, 2007.  
11. Daekyoung Jung, Wonjae Kim, Hyunjoo Song, Jeong-in Hwang, Bongshin Lee, Bohyoung Kim, and Jinwook Seo. “ChartSense: Interactive data extraction from chart images.” *CHI*, 2017.  
12. Kushal Kafle, Brian Price, Scott Cohen, and Christopher Kanan. “DVQA: Understanding data visualizations via question answering.” *CVPR*, 2018.  
13. Kushal Kafle, Robik Shrestha, Brian Price, Scott Cohen, and Christopher Kanan. “Answering questions about data visualizations using efficient bimodal fusion.” *arXiv:1908.01801*, 2019.  
14. Samira Ebrahimi Kahou, Vincent Michalski, Adam Atkinson, Ákos Kádár, Adam Trischler, and Yoshua Bengio. “FigureQA: An annotated figure dataset for visual reasoning.” *arXiv:1710.07300*, 2017.  
15. Hei Law and Jia Deng. “CornerNet: Detecting objects as paired keypoints.” *ECCV*, 2018.  
16. Wenbo Li, Zhicheng Wang, Binyi Yin, Qixiang Peng, Yuming Du, Tianzi Xiao, Gang Yu, Hongtao Lu, Yichen Wei, and Jian Sun. “Rethinking multi-stage networks for human pose estimation.” *arXiv:1901.00148*, 2019.  
17. Xiaoyi Liu, Diego Klabjan, and Patrick N. Bless. “Data extraction from charts via single deep neural network.” *arXiv:1906.11906*, 2019.  
18. Yan Liu, Xiaoqing Lu, Yeyang Qin, Zhi Tang, and Jianbo Xu. “Review of chart recognition in document images.” *Visualization and Data Analysis*, 8654:865410, 2013.  
19. Alejandro Newell, Kaiyu Yang, and Jia Deng. “Stacked hourglass networks for human pose estimation.” *ECCV*, 2016.  
20. Jorge Poco and Jeffrey Heer. “Reverse-engineering visualizations: Recovering visual encodings from chart images.” *Computer Graphics Forum*, 2017.  
21. Jorge Poco, Angela Mayhua, and Jeffrey Heer. “Extracting and retargeting color mappings from bitmap images of visualizations.” *IEEE Transactions on Visualization and Computer Graphics*, 24(1):637–646, 2018.  
22. Shaoqing Ren, Kaiming He, Ross Girshick, and Jian Sun. “Faster R-CNN: Towards real-time object detection with region proposal networks.” 2015.  
23. Manolis Savva, Nicholas Kong, Arti Chhajta, Fei-Fei Li, Maneesh Agrawala, and Jeffrey Heer. “Revision: Automated classification, analysis, and redesign of chart images.” *ACM Symposium on User Interface Software & Technology*, 2011.  
24. Sudhindra Shukla and Ashok Samal. “Recognition and quality assessment of data charts in mixed-mode documents.” *International Journal of Document Analysis and Recognition*, 11(3):111, 2008.  
25. Yue Wu, Tal Hassner, KangGeon Kim, Gerard Medioni, and Prem Natarajan. “Facial landmark detection with tweaked convolutional neural networks.” *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 40(12):3067–3074, 2017.

