import os
import shutil
import zipfile
from io import BytesIO

def save_uploaded_file(file, temp_path: str) -> None:
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

def create_zip(output_path: str,kick_path: str, plot_path: str) -> BytesIO:
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(output_path, "resultat_kicks_synchronise.wav")
        zip_file.write(kick_path, "temp_kick_loop.wav")
        zip_file.write(plot_path, "audio_plots.png")
    zip_buffer.seek(0)
    return zip_buffer