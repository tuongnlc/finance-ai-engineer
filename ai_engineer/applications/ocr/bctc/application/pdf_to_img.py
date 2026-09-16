import pymupdf
from pathlib import Path

class PDFToImg:
    """
    Convert pdf to img
    """
    def __init__(self, input_prefix_pdf_path, output_prefix_img_path, output_dir):
        self.input_prefix_pdf_path = input_prefix_pdf_path
        self.output_prefix_img_path = output_prefix_img_path
        self.output_dir = output_dir


    def _make_dir_if_not_exist(self):
        output_dir = Path(self.output_dir)
        output_dir.mkdir(exist_ok=True)
        return output_dir

    def _convert_pdf_to_img(self, pdf_len: int, dpi=300):
        output_dir = self._make_dir_if_not_exist()

        for i in range(1, pdf_len + 1):
            pdf_file_name = f"{self.input_prefix_pdf_path}/page_{i}.pdf"
            output_name = f"{self.output_prefix_img_path}_{i}"

            with pymupdf.open(pdf_file_name) as doc:
                for page_index in range(len(doc)):
                    page = doc[page_index]
                    try:
                        pix = page.get_pixmap(dpi=dpi, alpha=False)
                    except TypeError:
                        zoom=4
                        mat = pymupdf.Matrix(zoom, zoom)
                        pix = page.get_pixmap(matrix=mat, alpha=False)

                    pix.save(str(output_dir / f"{output_name}.png"))

    def run(self, pdf_len: int, dpi=300):
        self._convert_pdf_to_img(pdf_len, dpi)
