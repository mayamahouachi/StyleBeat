
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import os
from audio_processing import (
    load_audio_files, detect_beats, generate_envelope, apply_envelope,
    create_kick_loop, generate_final_song, generate_plots
)
from utils import save_uploaded_file, create_zip

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API"}

@app.post("/upload/")
async def upload_and_process_song(
    file: UploadFile = File(...),
    kick_file: str = "selected_beats/TechDHitA-Perc01.wav",
    attenuation_duration: float = 0.1
):
    temp_input_path = "temp_uploaded_song.wav"
    temp_attenuee_path = "temp_chanson_attenuee.wav"
    output_path = "resultat_kicks_synchronise.wav"
    plot_path = "audio_plots.png"
    kick_path = "temp_kick_loop.wav"
    save_uploaded_file(file, temp_input_path)

    if not os.path.exists(kick_file):
        raise FileNotFoundError(f"Le fichier kick {kick_file} n'est pas trouvé dans le répertoire.")

    chanson, kick, y_chanson, y_kick, sr = load_audio_files(temp_input_path, kick_file)
    beat_times = detect_beats(y_chanson, sr)
    envelope = generate_envelope(len(y_chanson), beat_times, sr, kick, attenuation_duration)
    chanson_attenuee = apply_envelope(y_chanson, envelope, sr, temp_attenuee_path)
    kick_loop = create_kick_loop(chanson, kick, beat_times)
    chanson_finale, y_chanson_finale, sr_final = generate_final_song(chanson_attenuee, kick_loop, output_path, gain_boost=3)
    generate_plots(y_chanson, sr, beat_times, envelope, kick_loop, y_chanson_finale, plot_path, attenuation_duration)
    zip_buffer = create_zip(output_path,kick_path, plot_path)

     # Cleaning
    os.remove(temp_input_path)
    os.remove(temp_attenuee_path)
    os.remove(output_path)
    os.remove(plot_path)
    os.remove(kick_path)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=audio_and_plots.zip"}
    )

# Lancer avec : uvicorn app:app --reload