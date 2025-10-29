import os
import wget


class PdfDownloader:
    """Класс для загрузки PDF-файлов."""

    def __init__(self, files_name_list, pdf_files_list):
        self.files_name_list = files_name_list
        self.pdf_files_list = pdf_files_list

    def execute(self, path):
        os.makedirs(path, exist_ok=True)
        for name, url in zip(self.files_name_list, self.pdf_files_list):
            dest = os.path.join(path, name)

            if os.path.exists(dest):
                continue
            wget.download(url, dest)
