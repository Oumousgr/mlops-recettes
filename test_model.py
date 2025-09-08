import joblib

model = joblib.load("model_recette.pkl")
# Test
ingredients_utilisateur = ["pâtes", "viande hachée", "tomate", "oignon"]

input_text = " ".join(ingredients_utilisateur)
prediction = model.predict([input_text])
print("Voici la recette suggérée :", prediction[0])
