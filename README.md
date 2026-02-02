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

---

# ChartOCR (upstream instructions)

Fork the code from the ChartOCR [github](https://github.com/soap117/DeepRule), and update the instructions for environment setup.

## Getting Started

Please first install [Anaconda](https://anaconda.org) and create an Anaconda environment using the provided package list.

```
conda create  --name DeepRule --file DeepRule.txt
```

After you create the environment, activate it.

```
source activate DeepRule
```

Our current implementation only supports GPU so you need a GPU and need to have CUDA installed on your machine.

### Compiling Corner Pooling Layers

You need to compile the C++ implementation of corner pooling layers.
Please check the latest [CornerNetLite](https://github.com/princeton-vl/CornerNet-Lite) on github if you find problems.

```
cd <CornerNetLite dir>/core/models/py_utils/_cpools/
python setup.py build_ext --inplace
```

### Compiling NMS

You also need to compile the NMS code (originally from [Faster R-CNN](https://github.com/rbgirshick/py-faster-rcnn/blob/master/lib/nms/cpu_nms.pyx) and [Soft-NMS](https://github.com/bharatsingh430/soft-nms/blob/master/lib/nms/cpu_nms.pyx)).

```
cd <CornerNetLite dir>/core/external
make
```

After this step, you also need to compile the NMS code in this github repo

```
cd external
make
```

### Installing MS COCO APIs

You also need to install the MS COCO APIs.

```
cd <CornerNet-Lite dir>
mkdir data
cd <CornerNet-Lite dir>/data
git clone git@github.com:cocodataset/cocoapi.git coco
cd <CornerNet-Lite dir>/data/coco/PythonAPI
make
```

### Downloading CHARTEX Data

- [Pie data](https://drive.google.com/file/d/1inUIjmRfgPJr9p90JIRTEBPv-ylxQmyD/view?usp=sharing)
- [Line data](https://drive.google.com/file/d/1bnuHyExM6JagB1caRfLVr20vef4nesi9/view?usp=sharing)
- [Bar data](https://drive.google.com/file/d/19Wt04WsnS1pNAffZqjpSBF-Klf4t3b9C/view?usp=sharing)
- [Cls data](https://drive.google.com/file/d/143_WZT_9_oozOxzWCxBfuxN1J1JKa3Kv/view?usp=sharing)
- Unzip the file to the data path

### Data Description (Updated on 11/21/2021)

- For Pie data<br/>
{"image_id": 74999, "category_id": 0, "bbox": [135.0, 60.0, 132.0, 60.0, 134.0, 130.0], "area": 105.02630551355209, "id": 433872}<br/>
The meaning of the bbox is [edge_1_x, edge_1_y, edge_2_x, edge_2_y,center_x, center_y]<br/>
It is the three critical points for a sector of the pie graph, the two sector adjacent points are ordered clock-wise.

- For the line data<br/>
{"image_id": 120596, "category_id": 0, "bbox": [137.0, 131.0, 174.0, 113.0, 210.0, 80.0, 247.0, 85.0], "area": 0, "id": 288282}<br/>
The meaning of the bbox is [d_1_x, d_1_y, ... d_n_x, d_n_y]<br/>
It is the data points for a line in the image with image_id.<br/>
instancesLineClsEx is used for training the LineCls.

- For the Bar data<br/>
Just the bounding box of the bars.

- For the cls data<br/>
Just the bounding box.<br/>
But different category_id refers to different components like the draw area, title and legends.

### OCR API (Updated on 08/17/2022)

I am longger working at the microsoft, many features rely on the webservice may be out of date.
The origninal OCR API requests the AZURE service. For people who do not have the AZURE service, pytesseract python pacakge may be a good replacment.
However, you need to rewrite ocr_result(image_path) funtion. The key output of this function is the bounding box of the words and the str version of the words.
E.g., word_info["text"]='Hello', word_info["boundingBox"] = [1, 2, 67, 78]
The boudningBox is the topleft_x, topleft_y, bottomleft_x, bottomlef_y.

### Downloading Trained File

- [data link](https://drive.google.com/file/d/1qtCLlzKm8mx7kQOV1criUbqcGnNh58Rr/view?usp=sharing)
- Unzip the file to current root path

## Training and Evaluation

To train and evaluate a network, you will need to create a configuration file, which defines the hyperparameters, and a model file, which defines the network architecture. The configuration file should be in JSON format and placed in `config/`. Each configuration file should have a corresponding model file in `models/`. i.e. If there is a `<model>.json` in `config/`, there should be a `<model>.py` in `models/`. There is only one exception which we will mention later.
The cfg file names of our proposed modules are as follows:

Bar: CornerNetPureBar

Pie: CornerNetPurePie

Line: CornerNetLine

Query: CornerNetLineClsReal

Cls: CornerNetCls

To train a model:

```
python train.py --cfg_file <model> --data_dir <data path>
e.g.
python train_chart.py --cfg_file CornerNetBar --data_dir /home/data/bardata(1031)
```

To use the trained model as a web server pipeline:

```
python manage.py runserver 8800
```

Access localhost:8800 to interact.

If you want to test batch of data directly, here you have to pre-assign the type of charts.

```
python test_pipe_type_cloud.py --image_path <image_path> --save_path <save_path> --type <type>
e.g.
python test_pipe_type_cloud.py --image_path /data/bar_test --save_path save --type Bar
```

## Instructions For Running Jupyter Notebook

To generate the table from the predicted keypoints of ChartOCR, you can run the jupyter notebook that I built for the three types of charts: bar, line, and pie. (The code for bar is still underdevelopment)

### Environment Set Up

Install [conda](https://docs.conda.io/en/latest/miniconda.html) and run the following command:

```
conda env create -f chart2table_env.yaml
```

After you run this command, you will have a conda environment setup named "chart2table". To activate the conda environment to run the jupyter notebook, run

```
conda activate chart2table
```

### Run Jupyter Notebook

Once, you activate the conda environment, run the following command to use the conda environment to run the jupyter notebook:

```
python -m ipykernel install --user --name=chart2table
```

After that, you can launch the jupyter notebook with

```
jupyter notebook --port=<Port Number>
```

The jupyter notebook will then be read to view and edit at localhost:<Port Number> on your local browser. You can then access the three jupyter notebooks for pie, line and bar chart2table conversion.

### Download the Chart Dataset

To run the jupyter notebook, you will also need the chart dataset from [here](https://drive.google.com/file/d/1wVSUuCOmcSt7t34MizX0yKgFX3ybM3zd/view?usp=sharing)
