import requests
import os

# Set token storage location
WIF_HOME = os.environ.get("WIF_HOME", "/tmp/wif")  # fallback default
WIF_TOKEN_FILENAME = os.path.join(WIF_HOME, "wif_token.txt")

# API endpoint
endpoint_url = "https://frog345byuo1.bb.cd.com:7001/get_wif_token"

# Certs and key
client_cert = ("client.crt", "client.key")  # tuple form: (cert, key)
ca_cert = "ca.crt"  # CA that signed the server cert

def get_token_from_endpoint():
    try:
        response = requests.get(
            endpoint_url,
            cert=client_cert,
            verify=ca_cert
        )
        response.raise_for_status()
        data = response.json()
        if "access_token" in data:
            return data["access_token"]
        else:
            print("Unexpected response format.")
            return None
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def write_content_to_file(filepath, content):
    if content:
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Token written to: {filepath}")
        except Exception as e:
            print(f"❌ Failed to write token: {e}")
    else:
        print("⚠️ No token to write.")

if __name__ == "__main__":
    token = get_token_from_endpoint()
    write_content_to_file(WIF_TOKEN_FILENAME, token)
