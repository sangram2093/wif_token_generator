✅ mTLS Setup: End-to-End Process (Fresh Start)
We'll split this into:

🔵 Part 1: Linux Server (Flask Token API)

🟢 Part 2: Local Client (App Team Machine)

🔵 PART 1 — LINUX SERVER: Secure Flask Token API with mTLS
🔧 Step 1: Directory Structure
bash
Copy
Edit
mkdir -p /opt/wif-token-api
cd /opt/wif-token-api
Place the following:

File	Purpose
server.crt	Server certificate (PEM)
server.key	Private key (unencrypted PEM)
intermediate.crt	Intermediate CA certificate
root-ca.crt	Root CA certificate

🔧 Step 2: Create Full CA Chain
Create ca-chain.crt with intermediate + root:

bash
Copy
Edit
cat intermediate.crt root-ca.crt > ca-chain.crt
🔧 Step 3: Flask Server Code (app.py)
python
Copy
Edit
import os
from flask import Flask, jsonify

app = Flask(__name__)
WIF_HOME = os.environ.get("WIF_HOME", "/tmp/wif")
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import ssl
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    context.load_verify_locations(cafile="ca-chain.crt")
    context.verify_mode = ssl.CERT_REQUIRED
    app.run(host="0.0.0.0", port=7001, ssl_context=context)
🔧 Step 4: Decrypt Server Key (Optional but Recommended)
If your server.key is encrypted:

bash
Copy
Edit
openssl rsa -in server.key -out server-decrypted.key
Then use server-decrypted.key in app.py.

✅ Step 5: Start Flask
bash
Copy
Edit
export WIF_HOME=/opt/wif-token-api
python3 app.py
Your API is now running at:

arduino
Copy
Edit
https://<server-host>:7001/get_wif_token
🟢 PART 2 — LOCAL CLIENT: App Team Setup
✅ Step 1: Generate Private Key and CSR
bash
Copy
Edit
openssl genrsa -out client.key 2048

openssl req -new -key client.key -out client.csr \
-subj "/CN=app-team-client/O=Internal/CD=cd/DC=com"
✅ Step 2: Upload CSR to Internal PKI
Upload client.csr

Request TLS client authentication

Download client.crt (PEM format)

✅ Step 3: Verify Key Pair Match
bash
Copy
Edit
openssl x509 -noout -modulus -in client.crt | openssl md5
openssl rsa  -noout -modulus -in client.key  | openssl md5
✅ Output must match.

✅ Step 4: Create client.pem (Optional: Combine cert + key)
bash
Copy
Edit
cat client.crt client.key > client.pem
✅ Step 5: Get the Root + Intermediate CA Certs
From your PKI team or internal trust store, download:

intermediate.crt

root-ca.crt

Then:

bash
Copy
Edit
cat intermediate.crt root-ca.crt > ca-chain.crt
✅ Step 6: Python Code (Client)
python
Copy
Edit
import requests
import os

WIF_HOME = os.environ.get("WIF_HOME", "/tmp/wif")
WIF_TOKEN_FILENAME = os.path.join(WIF_HOME, "wif_token.txt")

endpoint_url = "https://<server-host>:7001/get_wif_token"

client_cert = ("client.crt", "client.key")  # or "client.pem"
ca_cert = "ca-chain.crt"

def get_token_from_endpoint():
    try:
        response = requests.get(endpoint_url, cert=client_cert, verify=ca_cert)
        response.raise_for_status()
        return response.json().get("access_token", None)
    except requests.exceptions.SSLError as ssl_err:
        print(f"❌ SSL error: {ssl_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"❌ Request failed: {req_err}")
    return None

def write_token(filepath, content):
    if content:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Token written to {filepath}")
    else:
        print("⚠️ No token received.")

if __name__ == "__main__":
    token = get_token_from_endpoint()
    write_token(WIF_TOKEN_FILENAME, token)
✅ Step 7: Run the Client
bash
Copy
Edit
export WIF_HOME=/tmp/wif
python3 get_wif_token.py
✅ You should now see:

bash
Copy
Edit
✅ Token written to /tmp/wif/wif_token.txt
🧪 Test with curl (Optional)
bash
Copy
Edit
curl --cert client.crt --key client.key --cacert ca-chain.crt \
  https://<server-host>:7001/get_wif_token
🔐 Summary of Trust Chain
File	Purpose
client.crt	Client identity
client.key	Client's private key
ca-chain.crt	Server uses to validate client cert
server.crt	Server's public cert
server.key	Server's private key
ca-chain.crt	Client uses to validate server
