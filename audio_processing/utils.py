import os
import shutil
import zipfile
from io import BytesIO

def save_uploaded_file(file, temp_path: str) -> None:
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

