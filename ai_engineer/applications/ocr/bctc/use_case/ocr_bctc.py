import os
from ai_engineer.applications.ocr.bctc.application.pdf_spliter import PDFSplititer
from ai_engineer.applications.ocr.bctc.application.pdf_to_img import PDFToImg
from ai_engineer.applications.ocr.bctc.application.img_preprocessing_and_call_llm import ImgOCRBCTCPreprocessing
from ai_engineer.shared.llm.create_llm import create_gemini_llm
import time
import json



from dotenv import load_dotenv
load_dotenv()
# llm_api_key = os.getenv("GCP_PROJECT_8")
list_of_api_keys = [
    "GCP_PROJECT_1",
    "GCP_PROJECT_2",
    "GCP_PROJECT_3",
    "GCP_PROJECT_4",
    "GCP_PROJECT_5",
    "GCP_PROJECT_6",
    "GCP_PROJECT_7",
    "GCP_PROJECT_8",
]
import random

api_key = random.choice(list_of_api_keys)
api_key = os.getenv(api_key)

class OCRBCTCUseCase:
    def __init__(self, pdf_splititer: PDFSplititer, pdf_to_img: PDFToImg, img_preprocessing: ImgOCRBCTCPreprocessing):
        self.pdf_splititer = pdf_splititer
        self.pdf_to_img = pdf_to_img
        self.img_preprocessing = img_preprocessing

    def split_pdf(self):
        len_document, pdf_name = self.pdf_splititer.run()
        return len_document, pdf_name
    
    def convert_pdf_to_img(self, pdf_len: int):
        self.pdf_to_img.run(pdf_len)

    def preprocess_img(self, pdf_len: int):
        self.img_preprocessing.run(pdf_len)

    def run(self):
        start_time = time.time()
        len_document, pdf_name = self.split_pdf()
        end_time = time.time()
        split_time = end_time - start_time
        print(f"Split pdf done take {split_time} seconds.")
        print(f"pdf file {pdf_name} has {len_document} pages. Time: {split_time} seconds")

        start_time = time.time()
        self.convert_pdf_to_img(len_document)
        end_time = time.time()
        convert_time = end_time - start_time
        print(f"Convert pdf to img done take. Take {convert_time} seconds for {len_document} pages.")
        
        self.preprocess_img(len_document)
        print("Done preprocess img")

pdf_splititer = PDFSplititer(
    # input_pdf_path="/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/input_resources/test_2_bctc_hpg.pdf",
    input_pdf_path="/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/input_resources/bctc_vnm.pdf",
    output_dir="/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/preprocessing_resources/split_pdf",
)

pdf_to_img = PDFToImg(
    input_prefix_pdf_path="/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/preprocessing_resources/split_pdf",
    output_prefix_img_path="page_",
    output_dir="/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/preprocessing_resources/pdf_to_img",
)

llm = create_gemini_llm(
    api_key=api_key,
    model_name="gemini-3.1-flash-lite",
    temperature=0,
)

preprocessing_img = ImgOCRBCTCPreprocessing(
    llm=llm,
    prefix_input_img_url="/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/preprocessing_resources/pdf_to_img",
    prefix_output_img_url="/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/preprocessing_resources/img_preprocessing",
    output_txt_dir="/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/ocr/bctc/output_resources/vnm",
)

ocr_bctc_use_case = OCRBCTCUseCase(
    pdf_splititer=pdf_splititer,
    pdf_to_img=pdf_to_img,
    img_preprocessing=preprocessing_img,
)

ocr_bctc_use_case.run()