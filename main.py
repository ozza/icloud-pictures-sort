import os
import shutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from PIL import Image, ExifTags
import exiftool
from wand.image import Image as WandImage


def get_date(file_path):
    _, file_extension = os.path.splitext(file_path)
    image_extensions = [".jpg", ".jpeg", ".png"]
    video_extensions = [".mp4", ".mov", ".avi", ".3gp"]

    try:
        if file_extension.lower() in image_extensions:
            with Image.open(file_path) as img:
                exif_data = img._getexif()
                date_taken = exif_data.get(
                    36867
                )  # 36867 is the tag for DateTimeOriginal
                if date_taken:
                    return datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")

        elif file_extension.lower() == ".heic":
            with WandImage(filename=file_path) as img:
                date_taken = img.metadata.get("exif:DateTimeOriginal")
                if date_taken:
                    return datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")

        elif file_extension.lower() in video_extensions:
            with exiftool.ExifTool(executable="exiftool.exe") as et:
                metadata = et.get_metadata(file_path)
                media_created = metadata.get("QuickTime:MediaCreateDate")
                if media_created:
                    return datetime.strptime(media_created, "%Y:%m:%d %H:%M:%S")

        date_modified = os.path.getmtime(file_path)
        if date_modified:
            return datetime.fromtimestamp(date_modified)

        date_created = os.path.getctime(file_path)
        if date_created:
            return datetime.fromtimestamp(date_created)

    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")

    return None


def copy_file(file_path, dest_folder):
    date = get_date(file_path)
    if date:
        folder_name = date.strftime("%Y\\%B")
    else:
        folder_name = "Unknown"

    _, file_extension = os.path.splitext(file_path)
    doc_extensions = [".txt", ".doc", ".docx", ".pdf", ".odt"]

    if file_extension.lower() in doc_extensions:
        folder_name = "docs"

    new_folder_path = os.path.join(dest_folder, folder_name)

    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)

    shutil.copy2(file_path, new_folder_path)
    pbar.update(1)


def copy_files_to_new_directory(src_folder, dest_folder="Path/to/your/photos/folder"):
    if not os.path.exists(src_folder):
        print(f"Source folder '{src_folder}' does not exist.")
        return

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    all_files = []
    for dirpath, _, filenames in os.walk(src_folder):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            all_files.append(file_path)

    global pbar
    pbar = tqdm(total=len(all_files))

    with ThreadPoolExecutor(max_workers=5) as executor:
        for file_path in all_files:
            executor.submit(copy_file, file_path, dest_folder)

    pbar.close()


if __name__ == "__main__":
    src_folder = "Path/to/your/source/folder"
    copy_files_to_new_directory(src_folder)
