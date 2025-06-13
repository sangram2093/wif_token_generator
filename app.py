import os
from flask import Flask, jsonify, request

app = Flask(__name__)
WIF_HOME = os.environ.get("WIF_HOME")
WIF_TOKEN_FILENAME = os.path.join(WIF_HOME, "wif_token.txt")

@app.route("/")
def health_check():
    return jsonify({"status": "OK"}), 200

@app.route("/get_wif_token")
def get_token():
    try:
        with open(WIF_TOKEN_FILENAME, 'r') as f:
            token = f.read().strip()
            return jsonify({"access_token": token})
    except FileNotFoundError:
        return jsonify({"error": "Token file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import ssl
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    context.load_verify_locations(cafile="ca.crt")
    context.verify_mode = ssl.CERT_REQUIRED

    app.run(host="0.0.0.0", port=7001, ssl_context=context)
