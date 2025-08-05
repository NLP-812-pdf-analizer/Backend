import os
import gdown
from loguru import logger

# Скачивание файлов в текущую папку
def download_files():
    # Пример: файл "model.safetensors" из Google Drive
    file_url = "https://drive.google.com/drive/folders/1KqgJlybuhWlPsGu_UmRkCFWYXv3sILNk?usp=sharing"
    #output_path = "model.safetensors"  # Или любой другой путь в текущей папке
    output_folder = os.path.join(script_dir, "model")
    
    # Создаем папку, если она не существует
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"Скачиваю всю папку из Google Drive в {output_folder}...")
    gdown.download_folder(file_url, output=output_folder, quiet=False)

download_files()
files_list = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "model"))
logger.info(f"Готово! Скачанные файлы: {files_list}")
