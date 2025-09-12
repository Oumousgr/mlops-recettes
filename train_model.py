# train_model.py
import os
import unicodedata
import joblib
import pandas as pd
from typing import Tuple, Optional

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# --- MLflow / DagsHub ---
import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature
import dagshub

# Initialisation DagsHub / MLflow
dagshub.init(repo_owner="oumisangare", repo_name="mlops-recettes", mlflow=True)
mlflow.set_tracking_uri(
    os.getenv("MLFLOW_TRACKING_URI", "https://dagshub.com/oumisangare/mlops-recettes.mlflow")
)
mlflow.set_experiment("recettes-baseline")


def load_data(path: str = "recettes.csv") -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8")
    # Nettoyage défensif
    df["ingredients"] = df["ingredients"].fillna("").astype(str)
    df["recipe"] = df["recipe"].fillna("").astype(str)
    return df


def should_skip_split(y: pd.Series) -> bool:
    """On saute le split si dataset minuscule ou classes rares."""
    vc = y.value_counts()
    if len(y) < 8:
        return True
    if vc.min() < 2:
        return True
    return False


def build_pipeline() -> Pipeline:
    # TF-IDF + normalisation des accents, n-grammes (1,2) pour capter des paires
    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",  # "crème" -> "creme"
        ngram_range=(1, 2),
        min_df=1
    )
    clf = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    )
    return Pipeline([("vectorizer", vectorizer), ("classifier", clf)])


def train() -> None:
    df = load_data()
    X = df["ingredients"]
    y = df["recipe"]

    pipeline = build_pipeline()

    # Décider split ou non
    skip_split = should_skip_split(y)
    if skip_split:
        X_train, y_train = X, y
        X_test, y_test = None, None
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

    with mlflow.start_run():
        # Params
        mlflow.log_param("model", "LogisticRegression")
        mlflow.log_param("vectorizer", "Tfidf(1,2)")
        mlflow.log_param("class_weight", "balanced")
        mlflow.log_param("skip_split", skip_split)

        # Entraînement
        pipeline.fit(X_train, y_train)

        # Metrics
        acc_train = accuracy_score(y_train, pipeline.predict(X_train))
        mlflow.log_metric("accuracy_train", float(acc_train))

        if not skip_split and X_test is not None and len(X_test) > 0:
            acc_test = accuracy_score(y_test, pipeline.predict(X_test))
            mlflow.log_metric("accuracy_test", float(acc_test))
        else:
            acc_test = None  # pas de test pour mini-dataset

        # Sauvegarde locale pour l'API
        joblib.dump(pipeline, "model_recette.pkl")

        # Signature (sans input_example)
        _sample_in = ["pates tomate oignon"]
        signature = infer_signature(_sample_in, pipeline.predict(_sample_in))
        mlflow.sklearn.log_model(pipeline, artifact_path="model", signature=signature)

        if os.path.exists("recettes.csv"):
            mlflow.log_artifact("recettes.csv")

        print(
            f"Accuracy_train={acc_train:.3f} | "
            f"Accuracy_test={acc_test if acc_test is not None else 'NA'} | "
            f"Modèle sauvegardé dans model_recette.pkl"
        )


if __name__ == "__main__":
    train()
