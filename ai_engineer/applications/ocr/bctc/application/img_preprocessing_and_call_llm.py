import os
from pathlib import Path
from PIL import Image
import cv2 as cv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
import numpy as np
from pydantic import BaseModel
import pytesseract
import time


class OutputOCR(BaseModel):
    type_of_document: str
    type_of_content: str
    wrong_word: dict
    new_text: str

class ImgOCRBCTCPreprocessing():
    def __init__(self, llm, prefix_input_img_url: str, prefix_output_img_url: str, output_txt_dir: str, mapping_wrong_words: dict):
        self.llm = llm
        self.prefix_input_img_url = prefix_input_img_url
        self.prefix_output_img_url = prefix_output_img_url
        self.output_txt_dir = output_txt_dir
        self.mapping_wrong_words = mapping_wrong_words

    def _read_img(self, input_img_url: str):
        img = Image.open(input_img_url)
        img = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR) #convert image to bgr
        return img
    
    def _write_img(self, output_img_url: str, img):
        output_path = Path(output_img_url)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv.imwrite(str(output_path), img)

    def _detect_orientation(self, img):
        """
            Dùng để detect hướng ảnh
        """
        osd = pytesseract.image_to_osd(img, output_type=pytesseract.Output.DICT)
        rotate_deg = int(osd['rotate'])
        return rotate_deg

    def rotate_img(self, img):
        """
            Dùng để xoay ảnh theo góc (90, 180, 270 độ)
            angle: 90 = xoay theo chiều kim đồng hồ 90 độ
                180 = xoay 180 độ
                270 / -90 = xoay ngược chiều kim đồng hồ 90 độ
        """
        rotate_deg = self._detect_orientation(img)
        print(f"rotate_deg: {rotate_deg}")

        if rotate_deg == 0:
            return img, rotate_deg
        if rotate_deg == 90:
            img = cv.rotate(img, cv.ROTATE_90_CLOCKWISE)
        elif rotate_deg == 180:
            img = cv.rotate(img, cv.ROTATE_180)
        elif rotate_deg == 270 or rotate_deg == -90:
            img = cv.rotate(img, cv.ROTATE_90_COUNTERCLOCKWISE)
        else:
            raise ValueError(f"rotate_deg {rotate_deg} không được hỗ trợ. Chỉ hỗ trợ 90, 180, 270 (-90) độ.")
        
        return img, rotate_deg

    def _resize_img(self, img, scale=3):
        # return cv.resize(img, None, fx=scale, fy=scale, interpolation=cv.INTER_CUBIC) 
        return cv.resize(img, None, fx=scale, fy=scale, interpolation=cv.INTER_CUBIC) #nội suy trên mảng 4×4 pixel lân cận để tính màu pixel mới.

    def _convert_img_to_gray(self, img): #Not use now
        return cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    def _blur_img(self, img):
        """
            Làm mờ ảnh nhưng giữ độ nét của chữ
        """
        return cv.bilateralFilter(img, 9, 75, 75)

    def _remove_color_block(self, img, sat_thresh=70,
                       target_hue_ranges=((0, 10), (160, 180), (85, 130)),
                       remove_all_colors=False,
                       inpaint_radius=3):
        """
        Loại bỏ các vùng màu mục tiêu (đỏ: con dấu / xanh nước: chữ ký…) khỏi ảnh.
        img               : ảnh BGR 3 kênh (input bắt buộc phải là ảnh màu, không phải grayscale)
        sat_thresh        : ngưỡng saturation (bỏ qua các vùng xám/trắng/đen bão hòa thấp)
        target_hue_ranges : danh sách các khoảng hue cần loại bỏ trong HSV.
                            Mặc định: (0-10, 160-180) = đỏ ; (85-130) = xanh nước/chữ ký xanh đậm.
                            Ví dụ thêm các màu khác: vàng (20-38), lục (45-75), tím (140-160).
        remove_all_colors : True = loại TẤT CẢ các vùng có màu bão hòa cao (nhanh nhất, chỉ giữ chữ đen + nền trắng)
        inpaint_radius    : bán kính nội suy vùng bị xóa (làm mịn ranh giới)
        return            : ảnh grayscale đã loại bỏ vùng màu
        """
        if len(img.shape) != 3 or img.shape[2] != 3:
            raise ValueError("remove_color_block yêu cầu ảnh BGR 3 kênh làm input, không được truyền ảnh grayscale 1 kênh")

        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        h = hsv[:, :, 0]
        s = hsv[:, :, 1]

        # Các pixel có độ bão hòa màu đủ cao (chắc chắn là màu, không phải xám/trắng/đen)
        mask_high_sat = s > sat_thresh

        if remove_all_colors:
            mask = mask_high_sat
        else:
            # Ghép mask từ nhiều khoảng hue mục tiêu (đỏ, xanh nước…)
            mask_target = np.zeros_like(s, dtype=bool)
            for (lo, hi) in target_hue_ranges:
                mask_target |= (h >= lo) & (h <= hi)
            mask = mask_target & mask_high_sat

        # Morphology: mở rộng mask 1 chút để không bỏ sót viền nhạt của con dấu
        mask_uint8 = (mask.astype(np.uint8)) * 255
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
        mask_dilated = cv.dilate(mask_uint8, kernel, iterations=1)

        # Inpaint: nội suy từ vùng xung quanh thay vì vẽ trắng cứng → hạn chế gãy nét chữ
        result_bgr = cv.inpaint(img, mask_dilated, inpaintRadius=inpaint_radius, flags=cv.INPAINT_TELEA)

        final_gray = cv.cvtColor(result_bgr, cv.COLOR_BGR2GRAY)
        return final_gray

    def _preprocess_img(self, input_img_url, output_img_url):
        """
            Dùng để preprocess ảnh
        """
        
        img = self._read_img(input_img_url)
    
        print(f"processing img_url: {input_img_url}")

        img, rotate_deg = self.rotate_img(img)
        img = self._resize_img(img)
        img = self._remove_color_block(img)
        img = self._blur_img(img)

        # write output img
        # output_img_url = f"{self.prefix_output_img_url}/page__{i}.png"
        self._write_img(
            output_img_url=output_img_url,
            img=img
        )
        print(f"Done process img_url: {output_img_url}")
        print("")

        return img

    def _img_to_text(self, img):
        """
            Dùng để convert ảnh sang text
        """
        config = "--oem 1 --psm 4 --dpi 300 -c preserve_interword_spaces=10 -c tessedit_char_blacklist=▪•*■"
        text = pytesseract.image_to_string(img, lang="vie+eng", config=config)
        return text

    def _mapping_wrong_words(self, text: str, input_dict: dict):
        """
            Dùng để mapping các từ trong text sang các từ trong input_dict
        """
        for keyword, replacement in input_dict.items():
            text = text.replace(keyword, replacement)
        return text

    def _call_llm(self, text: str):
        parser = PydanticOutputParser(pydantic_object=OutputOCR)
        prompt_ = ChatPromptTemplate.from_messages(
        [
            (
                "user",
                "PERSONA Bạn là một chuyên gia tài chính, hiểu rõ các thuật ngữ tài chính, kinh tế.\n\n"
                + "[TASK]Nhiệm vụ của bạn là đoc đoạn văn tôi gửi và tiến hành những điều sau.\n"
                + "Bước 1: Đọc đoạn văn tôi gửi và cho tôi biết văn bản thường hay dạng bảng (type_of_document) với các thông số tài chính."
                + "Bước 2: Phân loại nội dung đoạn văn bản (type_of_content). Lựa chọn một trong các chủ đề sau: thông tin của doanh nghiệp, chỉ số tài chính, thuyết minh diễn giải.\n"
                + "Bước 3: Chuyển các từ đang bị sai chính tả, thiếu dấu thành tiếng việt có nghĩa\n"
                + "Bước 4: Cho tôi danh sách các từ đã chuyển thành tiếng việt có nghĩa dưới dạng json\n"
                + "Bước 5: Cho tôi đoạn văn đã chuyển thành tiếng việt có nghĩa (new_text). Output bắt buộc là dạng text.\n"
                + "[CONTEXT] Tuỳ thuộc vào phần nội dung ở bước 1 phía trên mà tiến hành\n" 
                + "Nếu văn bản thường: Chỉ cần chuyển các từ đang bị sai chính tả, thiếu dấu thành tiếng việt có nghĩa\n"
                + "Nếu văn bản dạng bảng: Đảm bảo các con số là chính xác.\n"
                + "Nếu văn bản có chứa bảng, Mỗi dòng văn bản là một hàng trong bảng. Luôn luôn giữ lại thông tin các con số (chỉ số tài chính). Cố gắng output đầu ra dễ dàng dựng lại thành bảng tài liệu\n"
                + " [FORMAT] Đầu ra bắt buộc phải là một đối tượng JSON hợp lệ, không kèm theo bất kỳ văn bản giải thích hay Markdown nào ngoài khối JSON. Theo sát EXAMPLE OUTPUT phía dưới {format_instructions}\n"
                + "--- START OF EXAMPLE ---\n"
                + "[EXAMPLE INPUT]\n"
                + "\n"
                + "\n"
                + "[EXAMPLE OUTPUT]\n"
                + "{{\n"
                + "    \"type_of_document\": \"table\",\n"
                + "    \"type_of_content\": \"thông tin của doanh nghiệp\",\n"
                + "\"wrong_word\": {{\n"
                + "    \"Cổ tc\": \"Cổ tức\",\n"
                + "    \"Cổ tuc\": \"Cổ tức\",\n"
                + "    \"Co tuc\": \"Cổ tức\"\n"
                + "}},\n"
                + "\"new_text\": \"Tích cực\"\n"
                + "}}\n"
                + "--- END OF EXAMPLE ---"
                + "\n"
                + "{text}",
            )
        ]
    ).partial(format_instructions=parser.get_format_instructions())
        
        structured_llm = self.llm.with_structured_output(OutputOCR)
        chain = prompt_ | structured_llm
        result: OutputOCR = chain.invoke({"text": text})
        print(result.model_dump_json(indent=4))

        return result.new_text

    def _save_as_txt_file(self, text: str, output_file_name: str, output_dir=None):
        #output_dir = '/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/test_ocr/output_text'
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, output_file_name)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)

    def run(self, pdf_len: int):
        for i in range (1, pdf_len + 1):
            input_img_url = f"{self.prefix_input_img_url}/page__{i}.png"
            output_img_url = f"{self.prefix_output_img_url}/page__{i}.png"
            start_time = time.time()
            img = self._preprocess_img(input_img_url, output_img_url)
            end_time = time.time()
            print(f"Preprocess img time: {end_time - start_time}")

            text = self._img_to_text(img)
            text = self._mapping_wrong_words(text, self.mapping_wrong_words)

            start_time = time.time()
            text = self._call_llm(text)
            end_time = time.time()
            print(f"Call LLM time: {end_time - start_time}")

            self._save_as_txt_file(text, output_file_name=f"ocr_result__page__{i}.txt", output_dir=self.output_txt_dir)
