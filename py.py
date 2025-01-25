from flask import Flask, request, redirect, jsonify,make_response
import jwt
import time
import os
from flask_cors import CORS 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
        "sub": "business@kyrusagency.com",  # User email or ID
        "name": "Kyrus",
        "email": "business@kyrusagency.com",
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

        # Print the received data (for debugging purposes)
        print(f"Received data: {data}")

        global shared_data1
        global shared_data2

        shared_data1 = data.get('email', None)  # Replace 'email' with the correct key name
        shared_data2 = data.get('name', None)


        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")

        # Initialize the WebDriver
        driver = webdriver.Chrome(options=options)

        # Load a page that redirects
        url = "https://kyrusagency.freshdesk.com/support/login?type=bot"  # This URL redirects 3 times before landing
        driver.get(url)

        # Print the final URL after redirection
        print(driver.current_url,flush=True)

        # Print the page content (if needed)
        cookies = driver.get_cookies()

        # Filter and print the specific cookies
        extracted_cookies = {}
        for cookie in cookies:
            if cookie['name'] in ['_helpkit_session', 'session_token']:
                extracted_cookies[cookie['name']] = cookie['value']
                print(f"{cookie['name']}: {cookie['value']}", flush=True)

        # Clean up
        driver.quit()
        # Respond with a confirmation message
        # If cookies were found, generate JavaScript to set them
        if extracted_cookies:
            # Prepare an array with both cookies
            cookies_array = [{"name": name, "value": value} for name, value in extracted_cookies.items()]
            
            # Return the cookies array as JSON
            return jsonify(cookies_array), 200, {'Content-Type': 'application/json'}


        # If no cookies found, return an error
        return jsonify({"error": "Required cookies not found!"}), 400
        

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

    



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use $PORT or default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)
