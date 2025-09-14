# MLOps – Recettes API

[![CI](https://github.com/Oumousgr/mlops-recettes/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Oumousgr/mlops-recettes/actions)
[![Docker Hub](https://img.shields.io/badge/DockerHub-oumou16%2Frecettes--api-blue)](https://hub.docker.com/r/oumou16/recettes-api)
[![DagsHub](https://img.shields.io/badge/DagsHub-mlops--recettes-brightgreen)](https://dagshub.com/oumisangare/mlops-recettes)

API Flask qui **suggère une recette** à partir d’une liste d’ingrédients, via un petit modèle ML (vectorisation `CountVectorizer` + `LogisticRegression`).

Le projet intègre :
- **DVC + DagsHub** pour la gestion du dataset `recettes.csv`
- **MLflow (DagsHub)** pour le tracking des runs
- **Docker** pour packager l’API
- **GitHub Actions (CI/CD)** : tests → build → push Docker → **déploiement local automatique** via un **webhook** exposé avec **ngrok**.

---

## Structure du dépôt

```
mlops-recettes/
├── app.py                    # API Flask: "/", "/predict", "/version"
├── train_model.py            # Entraînement + logging MLflow + export model_recette.pkl
├── test_model.py             # Tests unitaires modèle
├── tests/
│   └── test_api.py           # Tests API Flask (/predict)
├── recettes.csv              # Dataset (suivi par DVC)
├── recettes.csv.dvc          # Pointeur DVC du dataset
├── Dockerfile                # Image Docker de l’API
├── requirements.txt          # Dépendances Python
├── deploy_webhook.py         # Mini serveur Flask: déploie via webhook
├── .dvc/                     # Métadonnées DVC
├── .github/
│   └── workflows/
│       └── ci-cd.yml         # Pipeline CI/CD
└── README.md
```

---

## Prérequis

- **Windows 10/11**, PowerShell  
- **Python 3.11+**
- **Docker Desktop** (moteur Linux/WSL2)  
- **Git**
- **DVC** (`pip install dvc`)  
- **Ngrok 3.x** (`ngrok.exe`) — avec un `authtoken`

Comptes & dépôts :
- **GitHub** : `Oumousgr/mlops-recettes`
- **Docker Hub** : `oumou16/recettes-api`
- **DagsHub** : `oumisangare/mlops-recettes`  
  → Générer un **PAT** (token) sur DagsHub (ne pas publier dans le README).

---

## Installation locale

```powershell
# 1) Cloner
git clone https://github.com/Oumousgr/mlops-recettes.git
cd mlops-recettes

# 2) (Optionnel) Environnement virtuel
python -m venv .venv
. .venv/Scripts/Activate.ps1

# 3) Dépendances
pip install -r requirements.txt
```

---

## Données (DVC + DagsHub)

Le dataset `recettes.csv` est suivi par **DVC** et stocké sur **DagsHub**.

- Fichier attendu (exemple) :
  ```
  recipe,ingredients
  "Spaghetti bolognaise","pâtes tomate oignon viande hachée"
  "Soupe de courgettes","courgette oignon crème bouillon"
  ...
  ```

Synchroniser (si besoin) :
```powershell
# Pull des données depuis le remote DagsHub configuré
dvc pull

# Vérifier l’état
dvc status -c
```

> ⚠️ Les accès à DagsHub (DVC) sont configurés côté projet.

---

## Suivi des expériences (MLflow via DagsHub)

Le script d’entraînement logge automatiquement sur MLflow (DagsHub).  
Avant d’entraîner, définir **temporairement** les variables d’environnement (PowerShell) :

```powershell
$env:MLFLOW_TRACKING_URI = "https://dagshub.com/oumisangare/mlops-recettes.mlflow"
$env:MLFLOW_TRACKING_USERNAME = "oumisangare"
$env:MLFLOW_TRACKING_PASSWORD = "<PAT_DAGSHUB_À_DEMANDER_EN_PRIVÉ>"
```

---

## Entraîner le modèle

```powershell
python train_model.py
```

- Produit `model_recette.pkl` (chargé par l’API)
- Logge params/metrics/modèle dans MLflow (DagsHub)  
- Lien vers le run affiché en console.

---

## Lancer l’API en local

### 1) Sans Docker (développement)
```powershell
# Prérequis : model_recette.pkl présent (sinon, exécuter train_model.py)
python app.py
# ou (selon le script) : flask run --port 5000
```

### 2) Avec Docker
```powershell
# Construire l’image locale
docker build -t recettes-api:local .

# Lancer
docker run -d --rm -p 5000:5000 --name recettes-api `
  -e MLFLOW_TRACKING_URI="https://dagshub.com/oumisangare/mlops-recettes.mlflow" `
  -e MLFLOW_TRACKING_USERNAME="oumisangare" `
  -e MLFLOW_TRACKING_PASSWORD="<PAT_DAGSHUB_À_DEMANDER_EN_PRIVÉ>" `
  recettes-api:local
```

### 3) Tester
```powershell
# Santé
curl http://127.0.0.1:5000/
# Version déployée
curl http://127.0.0.1:5000/version

# Prédiction (PowerShell)
$body = @{ ingredients = @('pâtes','viande hachée','tomate','oignon') } | ConvertTo-Json -Compress
Invoke-RestMethod -Method POST -Uri 'http://127.0.0.1:5000/predict' -ContentType 'application/json; charset=utf-8' -Body $body
```

---

## CI/CD (GitHub Actions → Docker Hub → Déploiement local via webhook)

### Secrets requis (GitHub → Settings → Secrets and variables → Actions)

- `DOCKERHUB_USERNAME` : ex. `oumou16`
- `DOCKERHUB_TOKEN` : <TOKEN_DOCKERHUB_PRIVÉ>
- `DAGSHUB_USER` : `oumisangare`
- `DAGSHUB_TOKEN` : <PAT_DAGSHUB_PRIVÉ>
- `WEBHOOK_URL` : URL ngrok **+ `/deploy`** (ex. `https://XXXXXXXX.ngrok-free.app/deploy`)


Les valeurs réelles des tokens ne sont pas publiées. Me les demander en privé si nécessaire, ou utiliser vos propres comptes (Docker Hub / DagsHub) pour reproduire la CI/CD. 


### Pipeline
- Sur `push` sur `main` :
  1. Exécute les tests
  2. Build l’image Docker taggée avec le **SHA du commit**
  3. Push sur **Docker Hub** : `oumou16/recettes-api:<sha>`
  4. Appelle le **webhook** (voir ci-dessous) pour redémarrer l’API localement avec la nouvelle image

---

## Webhook de déploiement local (ngrok)

Ce mécanisme permet à GitHub Actions de **déployer chez vous**.

### Étapes locales (une seule fois par session)

**Terminal A – mini serveur de déploiement**
```powershell
# Lance le serveur qui écoute /deploy (port 9000)
python .\deploy_webhook.py
# -> reste ouvert
```

**Terminal B – ngrok (expose votre port 9000)**
```powershell
# Exemple générique (adapter le chemin vers ngrok.exe)
& "C:\chemin\vers\ngrok.exe" http 9000 --config "$env:USERPROFILE\.config\ngrok\ngrok.yml"

# Notez l’URL 'Forwarding', ex. :
https://XXXXXXXX.ngrok-free.app -> http://localhost:9000
```

**GitHub Secret `WEBHOOK_URL`**  
Mettre : `https://XXXXXXXX.ngrok-free.app/deploy`
# Dans GitHub → Secret WEBHOOK_URL = https://<URL_ngrok>/deploy
---

## Tests

```powershell
# Tests unitaires modèle et API
python -m pytest -q
```

---

## Endpoints

- `GET /` → “API Recettes en ligne”
- `GET /version` → version déployée (ex. `v2`)  
  > Astuce démo : incrémenter la valeur dans `app.py` pour valider les déploiements.
- `POST /predict`  
  **Body (JSON)** :
  ```json
  {
    "ingredients": ["pâtes", "tomate", "oignon", "viande hachée"]
  }
  ```
  **Réponse** :
  ```json
  { "recette_suggeree": "Spaghetti bolognaise" }
  ```

---

## Dépannage rapide

- **ngrok “agent too old”** : télécharger une v3 récente, configurer `authtoken`, fichier `~/.config/ngrok/ngrok.yml` avec `version: "3"`.
- **Webhook ne déploie pas** :  
  - Vérifier `deploy_webhook.py` actif + `ngrok` en ligne  
  - Vérifier le secret `WEBHOOK_URL` (bien `.../deploy`)  
  - Voir les logs GitHub Actions
- **Docker ne démarre pas** :  
  - Vérifier que `model_recette.pkl` est présent (sinon `python train_model.py`)  
  - Vérifier que `:5000` n’est pas occupé  
  - `docker logs recettes-api`

---

## Guide express 

1. **Lire** ce README (contexte & structure)
2. **Lancer** `train_model.py` (produit `model_recette.pkl`, logs MLflow)
3. **Démarrer** l’API (Docker recommandé)
4. **Tester** `/` , `/version` , `/predict`
5. **Verifications** Vérifier la CI sur GitHub Actions et l’image sur Docker Hub

---

## Licence

Projet pédagogique (usage éducatif).

---

### Auteur

- **Oumou** – repo GitHub : [Oumousgr/mlops-recettes](https://github.com/Oumousgr/mlops-recettes)
