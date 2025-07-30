import os
import gdown

# Установка gdown (если нет)
try:
    import gdown
except ImportError:
    os.system("pip install gdown")
    import gdown

# Скачивание файлов в текущую папку
def download_files():
    # Пример: файл "model.safetensors" из Google Drive
    file_url = "https://drive.google.com/drive/folders/1KqgJlybuhWlPsGu_UmRkCFWYXv3sILNk?usp=sharing"
    #output_path = "model.safetensors"  # Или любой другой путь в текущей папке
    #output_path = "" 
    
    #if not os.path.exists(output_path):
    print("Скачиваю всю папку из Google Drive...")
    gdown.download_folder(file_url, output=".", quiet=False)
    #else:
    #    print("Файлы уже загружены.")

if __name__ == "__main__":
    download_files()
    print("Готово! Файлы в текущей папке:")
    print(os.listdir())
