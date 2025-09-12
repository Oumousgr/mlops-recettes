from flask import Flask, request, jsonify
import joblib

# Charge le modèle une fois au démarrage
model = joblib.load("model_recette.pkl")

app = Flask(__name__)

@app.route("/")
def home():
    return "API Recettes en ligne"

# --- Nouveau endpoint pour vérifier la version déployée ---
@app.route("/version", methods=["GET"])
def version():
    return "v2"  # change la valeur (v3, v4, ...) pour valider les nouveaux déploiements

@app.route("/predict", methods=["POST"])
def predict():
    # silent=True évite un 415 si le Content-Type n'est pas JSON
    data = request.get_json(silent=True)

    if not data or "ingredients" not in data:
        return jsonify({"error": "Veuillez fournir une liste d'ingrédients"}), 400

    ingredients = data["ingredients"]
    if not isinstance(ingredients, list):
        return jsonify({"error": "Les ingrédients doivent être une liste"}), 400

    # Au cas où un élément ne serait pas une chaîne
    input_text = " ".join(map(str, ingredients))

    # Prédiction
    prediction = model.predict([input_text])
    return jsonify({"recette_suggeree": prediction[0]})

if __name__ == "__main__":
    app.run(debug=True)
