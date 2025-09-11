# train_model.py
import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# --- MLflow / DagsHub ---
import mlflow
import mlflow.sklearn  # pour log_model
from mlflow.models.signature import infer_signature
import dagshub

# Initialise l’intégration DagsHub (affiche l’URL de run dans la console)
dagshub.init(repo_owner="oumisangare", repo_name="mlops-recettes", mlflow=True)

# Utilise l’URI MLflow via env var si dispo, sinon force l’URL DagsHub
mlflow.set_tracking_uri(
    os.getenv("MLFLOW_TRACKING_URI",
              "https://dagshub.com/oumisangare/mlops-recettes.mlflow")
)

# Nom d’expérience (tu la verras dans l’onglet Experiments de DagsHub)
mlflow.set_experiment("recettes-baseline")


def load_data(path: str = "recettes.csv") -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8")


def train():
    df = load_data()
    X = df["ingredients"]
    y = df["recipe"]

    # Pipeline: vectorisation + modèle
    pipeline = Pipeline([
        ("vectorizer", CountVectorizer()),
        ("classifier", LogisticRegression(max_iter=1000))
    ])

    # --- Split robuste pour mini dataset ---
    value_counts = y.value_counts()
    can_stratify = (len(y) >= 4) and (value_counts.min() >= 2)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y if can_stratify else None
    )

    with mlflow.start_run():
        # ---- Params loggés
        mlflow.log_param("model", "LogisticRegression")
        mlflow.log_param("max_iter", 1000)
        mlflow.log_param("vectorizer", "CountVectorizer")
        mlflow.log_param("test_size", 0.25)
        mlflow.log_param("random_state", 42)
        mlflow.log_param("stratify", bool(can_stratify))
        mlflow.log_param("n_train", len(X_train))
        mlflow.log_param("n_test", len(X_test))

        # ---- Entraînement
        pipeline.fit(X_train, y_train)

        # ---- Évaluation
        if len(X_test) > 0:
            y_pred_test = pipeline.predict(X_test)
            acc_test = accuracy_score(y_test, y_pred_test)
            mlflow.log_metric("accuracy_test", float(acc_test))
        else:
            acc_test = None

        acc_train = accuracy_score(y_train, pipeline.predict(X_train))
        mlflow.log_metric("accuracy_train", float(acc_train))

        # ---- Sauvegarde locale (pour l’API)
        joblib.dump(pipeline, "model_recette.pkl")

        # ---- Signature uniquement (pas d'input_example pour éviter le warning)
        _sig_in = ["pâtes tomate oignon"]
        signature = infer_signature(_sig_in, pipeline.predict(_sig_in))

        mlflow.sklearn.log_model(
            pipeline,
            artifact_path="model",
            signature=signature
        )

        # (Optionnel) log du dataset utilisé
        if os.path.exists("recettes.csv"):
            mlflow.log_artifact("recettes.csv")

        print(
            f"Accuracy_test={acc_test if acc_test is not None else 'NA'} | "
            f"Accuracy_train={acc_train:.3f} | Modèle sauvegardé dans model_recette.pkl"
        )


if __name__ == "__main__":
    train()
