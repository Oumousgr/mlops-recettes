from flask import Flask, request, jsonify
import joblib

model = joblib.load("model_recette.pkl")

app = Flask(__name__)

@app.route("/")
def home():
    return "API Recettes en ligne"

@app.route("/version", methods=["GET"])
def version():
    return "v5"  

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)

    if not data or "ingredients" not in data:
        return jsonify({"error": "Veuillez fournir une liste d'ingrédients"}), 400

    ingredients = data["ingredients"]
    if not isinstance(ingredients, list):
        return jsonify({"error": "Les ingrédients doivent être une liste"}), 400

    input_text = " ".join(map(str, ingredients))

    # Prédiction
    prediction = model.predict([input_text])
    return jsonify({"Recette suggérée par votre thermomix :": prediction[0]})

if __name__ == "__main__":
    app.run(debug=True)
