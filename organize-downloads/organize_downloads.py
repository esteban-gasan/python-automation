import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    filename="organize_downloads.log",
    filemode="a",
    format="%(asctime)s %(levelname)s %(message)s"
)

SLEEP_MIN = 30
MB_LIMIT = 500
FILE_SIZE_LIMIT = MB_LIMIT * 1000000

# Appropriate folder for each file type
EXTENSION_FOLDERS = {
    'Data': ['csv', 'json', 'txt', 'xls', 'xlsx'],
    'Docs': ['doc', 'docx', 'ppt', 'pptx'],
    'Exe': ['exe'],
    'Images': ['jpg', 'jpeg', 'jpe', 'jif', 'jfif', 'jfi', 'png', 'gif', 'webp', 'tiff', 'svg', 'webp'],
    'Languages': ['c', 'cpp', 'json', 'py'],
    'Music': ['mp3', 'wav', 'flac'],
    'PDF': ['pdf'],
    'Videos': ['mp4', 'flv', 'mov', 'm4v', 'ts'],
    'Web': ['css', 'htm', 'html'],
    'Zips': ['zip', 'gz', 'rar'],
    'Other': [''],
}

if os.name == "nt":
    DOWNLOADS_FOLDER = f"{os.getenv('USERPROFILE')}\\Downloads"
else:
    DOWNLOADS_FOLDER = f"{os.getenv('HOME')}/Downloads"

downloads_path = Path(DOWNLOADS_FOLDER)


def main():
    while True:
        # Only get the files
        files = [
            item
            for item in downloads_path.iterdir()
            if item.is_file() and item.name != 'desktop.ini'
        ]
        for file in files:
            ext = file.suffix.strip('.').lower()
            folder = next(
                (k for k, v in EXTENSION_FOLDERS.items() if ext in v), None)
            if not folder:
                logging.warning(f'Folder for ".{ext}" not found ({file.name})')
                continue

            if (size := file.stat().st_size) > FILE_SIZE_LIMIT:
                logging.info(
                    f'"{file.name}" size: {size // 1000000} > {MB_LIMIT} MB')
                continue

            dest_path = downloads_path / folder
            Path(dest_path).mkdir(exist_ok=True)

            try:
                shutil.move(file.absolute(), dest_path)
            except shutil.Error as e:
                logging.info(e)
                now = datetime.now()
                # Rename file, adding current datetime, then move
                file = file.rename(os.path.join(
                    downloads_path,
                    f'{file.name.split(".")[0]}__{now.strftime("%Y-%m-%d_%H-%M-%S")}.{ext}'
                ))
                shutil.move(file.absolute(), dest_path)
            finally:
                logging.info(f'Moved "{file.name}" to {folder}')

        time.sleep(SLEEP_MIN * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script stopped by user")
        sys.exit(0)
