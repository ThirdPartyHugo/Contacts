from flask import Flask, request, redirect, jsonify
import jwt
import time
import os
from flask_cors import CORS 
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


PRIVATE_KEY = os.environ.get('PRIVATE_KEY')

FRESHDESK_SSO_URL = "https://servicevault.myfreshworks.com/sp/OIDC/800493065928406099/implicit"


# Send a GET request to the page
url = "https://kyrusagency.freshdesk.com/support/login"
response = requests.get(url)

# Check the response
if response.status_code == 200:
    print(response.text)  # HTML content
else:
    print(f"Failed to load page: {response.status_code}")

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

    
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

    
    redirect_url = f"{FRESHDESK_SSO_URL}?state={state}&id_token={token}"

    print(f"Redirecting user to: {redirect_url}")
    return redirect(redirect_url)

@app.route('/test', methods=['POST'])
def test_endpoint():
    try:
        # Get the JSON payload from the request
        data = request.get_json()

        # Print the received data (for debugging purposes)
        print(f"Received data: {data}")

        # Respond with a confirmation message
        return jsonify({"message": "Data received successfully!", "data": data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use $PORT or default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)
