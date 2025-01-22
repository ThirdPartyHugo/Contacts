from flask import Flask, request, redirect, jsonify
import jwt
import time
import os
import base64
import json

app = Flask(__name__)

PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAJSV0lvDePfGkjWr
I1tpPfkNbsD4JiqTN6qPqestJVo3xGvviICjdkOR2W64vgCwVpJhiaXnwlIJJ95m
yEMoHpFOad+oBqtcHxhRxcjxboDvcwxznH4qoeqN+B/p7Abm+qb88lQVTv7teclz
6G5p3nnhNz/IKS0qJ7DCZgODm6jVAgMBAAECgYAbu3rvtaQ2WtGfQrnurc3rVh59
1dMJz0BsjTPhuSNnm1EF9Ec9+0RviCFVERYlesQtvha66G7UcPEICZcHMc3CeAw0
srRLdxYKt+eG87zqTeJYg9obeBV1mdCh376vxeM5XrKu+2er4UFluFLpBihv4KgD
G+BK5Mr2zjR+NP93YQJBANW8O+2pF8C7bMqK8JevEYNw0wg0RJkQpL/ruhddHPub
7NKzx0LDTBv7UP8pyC6U8judl65q2HYynEdjSr1tDNMCQQCx94tOWkQsr9ASJkZz
c3aQE4DIRpXxpxZFIL842JfIe1+LmoR9r+DXlBckszxkx3plpPaLMIstuTt3l88t
s8q3AkAYPBKzfPPTh6zrPlvPZyteMwHKsVqB3JBBrrHYClfJ88EjlvzmBgzwM0vY
0tz+4yagOdtEDJtks5JiydBksCO/AkAudQR0i7PIRoz2b+9sK/QDYFP59BMoZgm2
OfoxCLl2qF4kv01e0g7Lt+jit7dIR5p39jw10ZJDeVtAuOxobcq5AkBBsb7VeThO
p5p4zeSB06qrJL4GF/hMW9W6aafNHuZqqBUCL6rRpxjUY8JY+0aO/0VaOoPhP8zp
N4nUaBkRIkpz
-----END PRIVATE KEY-----"""

FRESHDESK_SSO_URL = "https://servicevault.myfreshworks.com/sp/OIDC/800493065928406099/implicit"


@app.route('/sso/login', methods=['GET'])
def sso_login():
    # Capture all relevant query params
    client_id = request.args.get('client_id')       
    state = request.args.get('state')               
    nonce = request.args.get('nonce')               
    grant_type = request.args.get('grant_type')     
    scope = request.args.get('scope')               

    # Validate the important ones
    if not state or not nonce:
        return jsonify({"error": "Missing state or nonce"}), 400

    # Retrieve the GHL cookie from the browser
    #ghl_cookie = request.cookies.get('a')

    #if not ghl_cookie:
        #return jsonify({"error": "Missing GHL cookie"}), 400

    """try:
        # Decode the GHL cookie from Base64
        decoded_cookie = base64.b64decode(ghl_cookie).decode('utf-8')
        ghl_data = json.loads(decoded_cookie)

        # Extract the user_id and api_key
        ghl_user_id = ghl_data.get("userid")
        ghl_api_key = ghl_data.get("apikey")

        if not ghl_user_id or not ghl_api_key:
            return jsonify({"error": "Invalid GHL cookie data"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to process GHL cookie: {str(e)}"}), 400"""

    current_time = int(time.time())
    expiration_time = current_time + 900 

    # Generate a JWT payload
    payload = {
        "iat": current_time,
        "exp": expiration_time,
        "sub": "hpskate26@gmail.com",
        "name": "Hugo",
        "email": "hpskate26@gmail.com",
        "nonce": nonce
    }

    # Generate the JWT token
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

    # Redirect the user to the Freshdesk SSO URL
    redirect_url = f"{FRESHDESK_SSO_URL}?state={state}&id_token={token}"
    print(f"Redirecting user to: {redirect_url}")
    return redirect(redirect_url)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use $PORT or default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)
