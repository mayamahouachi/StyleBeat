from fastapi import FastAPI, UploadFile, File
import os
import shutil
from audio_processing import (
    load_audio_files, detect_beats, generate_envelope, apply_envelope,
    create_kick_loop, generate_final_song, generate_plots
)
from utils import save_uploaded_file

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
    # Chemins temporaires
    temp_input_path = "temp_uploaded_song.wav"
    temp_attenuee_path = "temp_chanson_attenuee.wav"
    
    # Chemins dans le dossier results
    results_dir = "results"
    output_path = os.path.join(results_dir, "resultat_final.wav")
    kick_path = os.path.join(results_dir, "kick_loop.wav")
    plot_path = os.path.join(results_dir, "audio_plots.png")

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    save_uploaded_file(file, temp_input_path)

    # Vérifier l'existence du fichier kick
    if not os.path.exists(kick_file):
        raise FileNotFoundError(f"Le fichier kick {kick_file} n'est pas trouvé dans le répertoire.")

    # Traitement audio
    chanson, kick, y_chanson, y_kick, sr = load_audio_files(temp_input_path, kick_file)
    beat_times = detect_beats(y_chanson, sr)
    envelope = generate_envelope(len(y_chanson), beat_times, sr, kick, attenuation_duration)
    chanson_attenuee = apply_envelope(y_chanson, envelope, sr, temp_attenuee_path)
    # Appel corrigé avec sr et dépaquetage du tuple
    kick_loop, y_kick_loop = create_kick_loop(chanson, kick, beat_times, kick_path, sr)
    chanson_finale, y_chanson_finale, sr_final = generate_final_song(chanson_attenuee, kick_loop, output_path, gain_boost=3)
    # Passage de y_kick_loop à generate_plots
    generate_plots(y_chanson, sr, beat_times, envelope, kick_loop, y_kick_loop, y_chanson_finale, plot_path, attenuation_duration)
    # Nettoyage des fichiers temporaires
    os.remove(temp_input_path)
    os.remove(temp_attenuee_path)

    # Les fichiers output_path, kick_path et plot_path sont maintenant dans results/
    return {"message": "Traitement terminé avec succès", "results_dir": results_dir}

# Lancer avec : uvicorn app:app --reload