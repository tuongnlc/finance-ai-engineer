import os
import pymupdf 


class PDFSplititer:
    def __init__(self, input_pdf_path, output_dir):
        self.input_pdf_path = input_pdf_path
        self.output_dir = output_dir
        pass

    def _split_pdf(self):
        os.makedirs(self.output_dir, exist_ok=True)
        doc = pymupdf.open(self.input_pdf_path)

        # get name of pdf file and length of pdf file
        pdf_name = os.path.basename(self.input_pdf_path).split(".")[0]
        page_count = len(doc)

        for i in range(page_count):
            new_doc = pymupdf.open()
            new_doc.insert_pdf(doc, from_page=i, to_page=i)
            output_path = os.path.join(self.output_dir, f"page_{i + 1}.pdf")
            new_doc.save(output_path)
            new_doc.close()

        doc.close()
        return page_count, pdf_name

    def run(self):
        return self._split_pdf()
