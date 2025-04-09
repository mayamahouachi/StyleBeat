import librosa
import pydub
from pydub import AudioSegment
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

def load_audio_files(song_path: str, kick_path: str):
    chanson = AudioSegment.from_file(song_path)
    kick = AudioSegment.from_file(kick_path)
    y_chanson, sr = librosa.load(song_path)
    y_kick, _ = librosa.load(kick_path, sr=sr)
    return chanson, kick, y_chanson, y_kick, sr

def detect_beats(y_chanson: np.ndarray, sr: int):
    tempo, beats = librosa.beat.beat_track(y=y_chanson, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    print(f"Nombre de pics détectés : {len(beat_times)}")
    print(f"Positions des pics (s) : {beat_times[:5]}...")
    return beat_times

def generate_envelope(total_samples: int, beat_times: np.ndarray, sr: int, kick: AudioSegment, attenuation_duration: float):
    envelope = np.ones(total_samples)
    kick_duration_s = len(kick) / 1000  
    effective_duration = min(attenuation_duration, kick_duration_s)  
    decay_samples = int(effective_duration * sr)

    for beat_time in beat_times:
        start_sample = int(beat_time * sr - decay_samples / 2) 
        if start_sample < 0:
            start_sample = 0
        end_sample = min(start_sample + decay_samples, total_samples)

        # Courbe sinusoïdale 
        if end_sample > start_sample:
            t = np.linspace(0, np.pi, end_sample - start_sample)  # De 0 à π pour une demi-sinusoïde inversée
            decay = 1 - 0.9 * np.sin(t)  # De 1 à 0.1 (minimum) puis retour à 1
            envelope[start_sample:end_sample] = np.minimum(envelope[start_sample:end_sample], decay)

    return envelope

def apply_envelope(y_chanson: np.ndarray, envelope: np.ndarray, sr: int, temp_path: str):
    y_chanson_attenuee = y_chanson * envelope
    y_chanson_attenuee = y_chanson_attenuee / np.max(np.abs(y_chanson_attenuee)) * np.max(np.abs(y_chanson))
    sf.write(temp_path, y_chanson_attenuee, sr, subtype='PCM_16')
    return AudioSegment.from_file(temp_path)

def create_kick_loop(chanson: AudioSegment, kick: AudioSegment, beat_times: np.ndarray, output_path: str):
    duree_chanson_ms = len(chanson)
    kick_loop = AudioSegment.silent(duration=duree_chanson_ms)
    for beat_time in beat_times:
        pos_ms = int(beat_time * 1000)
        kick_loop = kick_loop.overlay(kick, position=pos_ms)
    kick_loop.export(output_path, format="wav")

    return kick_loop

def generate_final_song(chanson_attenuee: AudioSegment, kick_loop: AudioSegment, output_path: str, gain_boost: int = 3):
    chanson_finale = chanson_attenuee.overlay(kick_loop)
    chanson_finale = chanson_finale + gain_boost
    chanson_finale.export(output_path, format="wav")
    y_chanson_finale, sr = librosa.load(output_path)
    return chanson_finale, y_chanson_finale, sr

def generate_plots(y_chanson: np.ndarray, sr: int, beat_times: np.ndarray, envelope: np.ndarray, 
                   kick_loop: AudioSegment, y_chanson_finale: np.ndarray, plot_path: str, attenuation_duration: float):
    plt.figure(figsize=(15, 10))

    plt.subplot(4, 1, 1)
    plt.plot(np.linspace(0, len(y_chanson) / sr, len(y_chanson)), y_chanson, alpha=0.3, color="blue")
    plt.title("Chanson originale")
    for beat_time in beat_times:
        plt.axvline(x=beat_time, color="green", linestyle="--", alpha=0.7)

    plt.subplot(4, 1, 2)
    plt.plot(np.linspace(0, len(y_kick_loop) / sr, len(y_kick_loop)), y_kick_loop, color="orange")
    plt.title("Boucle de kicks")
    for beat_time in beat_times:
        plt.axvline(x=beat_time, color="green", linestyle="--", alpha=0.7)

    plt.subplot(4, 1, 3)
    plt.plot(np.linspace(0, len(y_chanson) / sr, len(y_chanson)), envelope, color="red", linewidth=2)
    plt.title(f"Enveloppe appliquée (atténuation {attenuation_duration}s)")
    for beat_time in beat_times:
        plt.axvline(x=beat_time, color="green", linestyle="--", alpha=0.7)

    plt.subplot(4, 1, 4)
    plt.plot(np.linspace(0, len(y_chanson_finale) / sr, len(y_chanson_finale)), y_chanson_finale, alpha=0.3, color="purple")
    plt.title("Chanson finale")
    for beat_time in beat_times:
        plt.axvline(x=beat_time, color="green", linestyle="--", alpha=0.7)

    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()