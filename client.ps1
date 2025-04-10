# Lancer le client (front-end) avec http.server depuis la racine
Write-Host "Lancement du client HTTP..."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m http.server 9000" -WorkingDirectory "."