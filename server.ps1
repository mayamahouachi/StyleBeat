
# Lancer le serveur (back-end) dans audio_processing
Write-Host "Lancement du serveur FastAPI..."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m uvicorn main:app --reload --port 8000" -WorkingDirectory ".\audio_processing"

