from flask import Flask, request, redirect, jsonify,make_response
import jwt
import time
import os
from flask_cors import CORS 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from playwright.sync_api import sync_playwright

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


PRIVATE_KEY = os.environ.get('PRIVATE_KEY')

FRESHDESK_SSO_URL = "https://servicevault.myfreshworks.com/sp/OIDC/800493065928406099/implicit"

shared_data1 = None
shared_data2 = None


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
    expiration_time = current_time + 900  # Token expires in 15 minutes
    print(shared_data1,flush=True)
    # Generate a JWT payload
    
    payload = {
        "iat": current_time,
        "exp": expiration_time,
        "sub": shared_data1,  # User email or ID
        "name": shared_data2,
        "email": shared_data1,
        "nonce": nonce
    }

    # Generate JWT token
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

    # Store the JWT token in a session cookie
    print(f"Redirecting user to: {FRESHDESK_SSO_URL}?state={state}&id_token={token}",flush=True)
    print(token,flush=True)
    response = make_response(redirect(f"{FRESHDESK_SSO_URL}?state={state}&id_token={token}"))

    
    return response


@app.route('/test', methods=['POST'])
def test_endpoint():
    try:
        # Get the JSON payload from the request
        data = request.get_json()
        print(f"Received data: {data}")

        # Extract shared data (if needed)
        shared_data1 = data.get('email', None)
        shared_data2 = data.get('name', None)

        # Use Playwright instead of Selenium
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            context.set_default_navigation_timeout(15000)  # Set a timeout of 15 seconds
            
            # Block unnecessary resources (images, fonts, etc.)
            context.route("**/*", lambda route: route.continue_() if route.request.resource_type in ["document", "script", "xhr"] else route.abort())
            
            page = context.new_page()
            
            # Navigate to the URL
            url = "https://kyrusagency.freshdesk.com/support/login?type=bot"
            page.goto(url)

            # Wait for page to finish loading
            page.wait_for_load_state("networkidle")

            # Extract cookies
            cookies = page.context.cookies()
            extracted_cookies = {cookie['name']: cookie['value'] for cookie in cookies if cookie['name'] in ['_helpkit_session', 'session_token']}
            
            browser.close()

        # Return the cookies if found
        if extracted_cookies:
            cookies_array = [{"name": name, "value": value} for name, value in extracted_cookies.items()]
            return jsonify(cookies_array), 200, {'Content-Type': 'application/json'}

        # If no cookies found, return an error
        return jsonify({"error": "Required cookies not found!"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

    



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use $PORT or default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)
