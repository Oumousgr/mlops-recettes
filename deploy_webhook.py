from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

APP_PORT = os.getenv("APP_PORT", "5000")
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "recettes-api")
DEFAULT_IMAGE = os.getenv("IMAGE_NAME", "oumou16/recettes-api")
DEFAULT_TAG = os.getenv("IMAGE_TAG", "latest")


def run(cmd: str, check: bool = True):
    print("+", cmd)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr:
        print(res.stderr.strip())
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
    return res


@app.route("/health", methods=["GET"])
def health():
    return "ok", 200


@app.route("/deploy", methods=["POST"])
def deploy():
    data = request.get_json(silent=True) or {}
    image = data.get("image", DEFAULT_IMAGE)
    tag = data.get("tag", DEFAULT_TAG)
    full_image = f"{image}:{tag}"

    try:
        run(f"docker rm -f {CONTAINER_NAME}", check=False)
        run(f"docker pull {full_image}")
        env_flags = []
        for k in ["MLFLOW_TRACKING_URI", "MLFLOW_TRACKING_USERNAME", "MLFLOW_TRACKING_PASSWORD"]:
            if os.getenv(k):
                env_flags.append(f'-e {k}="{os.getenv(k)}"')
        env_str = " ".join(env_flags)

        run(
            f"docker run -d --rm -p 5000:5000 --name {CONTAINER_NAME} "
            f"{env_str} {full_image}"
        )

        return jsonify({"status": "ok", "image": full_image}), 200

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000)
