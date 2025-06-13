import requests
import os

WIF_HOME = os.environ.get("WIF_HOME")
WIF_TOKEN_FILENAME = os.path.join(WIF_HOME, "wif_token.txt")

endpoint_url = "https://frog345byuo1.bb.cd.com:7001/get_wif_token"

client_cert = ("client.crt", "client.key")
ca_cert = "ca.crt"

def get_token_from_endpoint():
    try:
        response = requests.get(endpoint_url, cert=client_cert, verify=ca_cert)
        response.raise_for_status()
        return response.json().get("access_token", None)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def write_content_to_file(filepath, content):
    if content:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Token written to {filepath}")

if __name__ == "__main__":
    token = get_token_from_endpoint()
    write_content_to_file(WIF_TOKEN_FILENAME, token)
