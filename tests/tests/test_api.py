import app as app_module

def test_home_ok():
    client = app_module.app.test_client()
    r = client.get("/")
    assert r.status_code == 200
    assert "API Recettes" in r.get_data(as_text=True)

def test_predict_ok():
    client = app_module.app.test_client()
    payload = {"ingredients": ["pâtes", "viande hachée", "tomate", "oignon"]}
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    data = r.get_json()
    assert "recette_suggeree" in data
    assert isinstance(data["recette_suggeree"], str)

def test_predict_bad_request():
    client = app_module.app.test_client()
    r = client.post("/predict", json={"wrong": []})
    assert r.status_code == 400
