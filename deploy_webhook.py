from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route("/deploy", methods=["POST"])
def deploy():
    data = request.get_json() or {}
    image = data.get("image")
    if not image:
        return jsonify({"error": "Missing 'image' in payload"}), 400
    try:
        subprocess.run(["docker", "rm", "-f", "recettes-api"], check=False)
        subprocess.run(["docker", "pull", image], check=True)
        subprocess.run(["docker", "run", "-d", "--name", "recettes-api", "-p", "5000:5000", image], check=True)
        return jsonify({"status": "ok", "image": image})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def health():
    return "webhook up"

if __name__ == "__main__":
    app.run(port=9000)
