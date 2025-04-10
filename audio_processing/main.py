from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
from audio_processing import (
    load_audio_files, detect_beats, generate_envelope, apply_envelope,
    create_kick_loop, generate_final_song, generate_plots
)
from utils import save_uploaded_file

app = FastAPI()

app.mount("/results", StaticFiles(directory="results"), name="results")
app.mount("/selected_beats", StaticFiles(directory="selected_beats"), name="beats")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000", "http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    print("GET / reçu")
    return {"message": "Bienvenue sur l'API"}

@app.options("/upload/")
async def options_upload():
    print("OPTIONS /upload/ reçu")
    return JSONResponse(content={"message": "OPTIONS OK"}, status_code=200)

@app.post("/upload/")
async def upload_and_process_song(
    kick_name: str = Form(...),  
    file: UploadFile = File(...),
    attenuation_duration: float = 0.1
):
    kick_file = "selected_beats/" + kick_name
    print("kick_file : ", kick_file)
    print("POST /upload/ reçu")
    print('Fichier reçu :', file.filename)
    print(f"Beat : kick_file : {kick_file}")
    
    if kick_file is None:
        return JSONResponse(
            content={"error": "Le paramètre 'kick_file' est manquant."},
            status_code=400
        )
    
    print(f"POST /upload/ reçu avec kick_file : {kick_file}")
    temp_input_path = "temp_uploaded_song.wav"
    temp_attenuee_path = "temp_chanson_attenuee.wav"
    
    results_dir = "results"
    output_path = os.path.join(results_dir, "resultat_kicks_synchronise.wav")
    kick_loop_path = os.path.join(results_dir, "temp_kick_loop.wav")  # Chemin du kick loop généré
    plot_path = os.path.join(results_dir, "audio_plots.png")

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"Dossier {results_dir} créé")

    save_uploaded_file(file, temp_input_path)

    kick_full_path = kick_file
    if not os.path.exists(kick_full_path):
        raise FileNotFoundError(f"Le fichier kick {kick_full_path} n'est pas trouvé.")

    # Traitement audio
    chanson, kick, y_chanson, y_kick, sr = load_audio_files(temp_input_path, kick_full_path)
    beat_times = detect_beats(y_chanson, sr)
    print(f"Nombre de pics détectés : {len(beat_times)}")
    print(f"Positions des pics (s) : {beat_times[:5]}...")
    envelope = generate_envelope(len(y_chanson), beat_times, sr, kick, attenuation_duration)
    chanson_attenuee = apply_envelope(y_chanson, envelope, sr, temp_attenuee_path)
    kick_loop, y_kick_loop = create_kick_loop(chanson, kick, beat_times, kick_loop_path, sr)  # Générer le kick loop
    chanson_finale, y_chanson_finale, sr_final = generate_final_song(chanson_attenuee, kick_loop, output_path)
    generate_plots(y_chanson, sr, beat_times, envelope, kick_loop, y_kick_loop, y_chanson_finale, plot_path, attenuation_duration)

    if os.path.exists(output_path):
        print(f"Fichier généré avec succès : {output_path}")
    else:
        print(f"Erreur : Fichier {output_path} non généré")

    if os.path.exists(kick_loop_path):
        print(f"Kick loop généré avec succès : {kick_loop_path}")
    else:
        print(f"Erreur : Kick loop {kick_loop_path} non généré")

    # Nettoyage des fichiers temporaires
    os.remove(temp_input_path)
    os.remove(temp_attenuee_path)

    print("POST /upload/ terminé")
    return {
        "message": "Traitement terminé avec succès",
        "results_dir": results_dir,
        "output_path": "results/resultat_kicks_synchronise.wav",
        "kick_loop_path": "results/temp_kick_loop.wav",  
        "plot_path": "results/audio_plots.png"
    }