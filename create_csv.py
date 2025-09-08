import pandas as pd

data = {
    "recipe": [
        "Poulet au curry",
        "Salade de tomates",
        "Spaghetti bolognaise",
        "Omelette au fromage",
        "Riz sauté aux légumes",
        "Gratin dauphinois",
        "Tarte aux pommes",
        "Pizza margherita",
        "Soupe de courgettes",
        "Sandwich thon mayo"
    ],
    "ingredients": [
        "poulet, curry, crème, oignon",
        "tomates, huile d'olive, sel",
        "pâtes, viande hachée, tomate, oignon",
        "œufs, fromage, lait, sel",
        "riz, carotte, poivron, sauce soja",
        "pommes de terre, crème, ail, fromage",
        "pommes, pâte brisée, sucre, cannelle",
        "pâte à pizza, tomate, mozzarella, basilic",
        "courgette, oignon, crème, bouillon",
        "pain, thon, mayonnaise, salade"
    ]
}

df = pd.DataFrame(data)
df.to_csv("recettes.csv", index=False, encoding="utf-8")
print("Fichier recettes.csv créé")
