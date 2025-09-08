# 1. Base Python légère
FROM python:3.11-slim

# 2. Éviter les .pyc et forcer stdout à flusher (logs immédiats)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Installer dépendances système minimales (build & locales)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Créer le dossier app
WORKDIR /app

# 5. Copier les dépendances en premier (cache des layers)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copier le code et les artefacts du modèle
COPY app.py /app/app.py
COPY model_recette.pkl /app/model_recette.pkl

# (optionnel) Si tu veux aussi garder le CSV:
# COPY recettes.csv /app/recettes.csv

# 7. Exposer le port
EXPOSE 5000

# 8. Lancer l'app avec gunicorn (bind sur 0.0.0.0 pour accès depuis l’hôte)
# "app:app" = fichier app.py et objet Flask nommé app
CMD ["python", "-m", "gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]

