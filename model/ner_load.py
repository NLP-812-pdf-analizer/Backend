import os
import gdown
from loguru import logger

# Скачивание файлов в текущую папку
def download_files():
    # Пример: файл "model.safetensors" из Google Drive
    file_url = "https://drive.google.com/drive/folders/1KqgJlybuhWlPsGu_UmRkCFWYXv3sILNk?usp=sharing"

    # Путь к текущей папке (где лежит .py файл)
    output_folder = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Скачиваю файлы в {output_folder}...")
    gdown.download_folder(file_url, output=output_folder, quiet=False)

download_files()
#files_list = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "model"))
files_list = os.listdir(os.path.dirname(os.path.abspath(__file__)))
logger.info(f"Готово! Скачанные файлы: {files_list}")
