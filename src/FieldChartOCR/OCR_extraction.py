#Extract OCR Text for ChartExcel Dataset
import os
import json
from paddleocr import PaddleOCR,draw_ocr
from tqdm import tqdm

ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, ocr_version="PP-OCRv3", enable_mkldnn=True)

def extract_ocr(chart_data_path):
	chart_image_path = f"{chart_data_path}/images"
	annotation_files = os.listdir(f'{chart_data_path}/annotations')

	for a in annotation_files:
		current_split = a.split('.')[0].split('_')[-1]
		assert current_split in ['train2019', 'val2019', 'test2019']
		chart_image_split_path = f"{chart_image_path}/{current_split}"

		tgt_dir = f'{chart_data_path}/ocr_results/{current_split}'
		#create the target directories
		os.makedirs(tgt_dir, exist_ok=True)

		#load the annotations
		current_annotation_path = f"{chart_data_path}/annotations/{a}"
		with open(current_annotation_path, 'r') as f:
			current_chart_annotation = json.load(f)


		#iterate through images
		for img_info in tqdm(current_chart_annotation['images']):
			filename = img_info['file_name']
			img_id = img_info['id']
			full_img_path = f'{chart_image_split_path}/{filename}'
			
			ocr_texts = ocr.ocr(full_img_path, cls=True)
			if len(ocr_texts) > 0:
				dest_path = f"{tgt_dir}/{img_id}.json"
				with open(dest_path, "w") as f:
					json.dump(ocr_texts, f)
				

if __name__ == "__main__":
	data_path = '/dvmm-filer2/projects/mingyang/semafor/chart_table/data'
	bar_path = f'{data_path}/bar'
	pie_path = f'{data_path}/pie'
	line_path = f'{data_path}/line'
    
	print("Extracting the Table Information from Pie Images")
	extract_ocr(pie_path)

	print("Extracting the Table Information from Bar Images")
	extract_ocr(bar_path)

	print("Extracting the Table Information from Line Images")
	extract_ocr(line_path)


	