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
    output_folder = os.path.join(script_dir, "model")
    
    # Создаем папку, если она не существует
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"Скачиваю всю папку из Google Drive в {output_folder}...")
    gdown.download_folder(file_url, output=output_folder, quiet=False)

if __name__ == "__main__":
    download_files()
    print("Готово! Скачанные файлы:")
    # Показываем содержимое папки model
    print(os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")))
