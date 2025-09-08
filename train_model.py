import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib


df = pd.read_csv("recettes.csv")
X = df["ingredients"]
y = df["recipe"]

# Créer un pipeline : vectorisation + modèle **RB**
model = Pipeline([
    ("vectorizer", CountVectorizer()),
    ("classifier", LogisticRegression())
])

model.fit(X, y)

# Sauvegarder le modèle dans un fichier .pkl **RB pq .plk**
joblib.dump(model, "model_recette.pkl")
print("Modèle entraîné et sauvegardé dans model_recette.pkl")
