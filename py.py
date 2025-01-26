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
    expiration_time = current_time + 900  
    
    payload = {
        "iat": current_time,
        "exp": expiration_time,
        "sub": shared_data1,  
        "name": shared_data2,
        "email": shared_data1,
        "nonce": nonce
    }

    # Generate JWT token
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

    response = make_response(redirect(f"{FRESHDESK_SSO_URL}?state={state}&id_token={token}"))

    
    return response


@app.route('/test', methods=['POST'])
def test_endpoint():

    try:
        
        data = request.get_json()

        global shared_data1
        global shared_data2

        shared_data1 = data.get('email', None)  # Replace 'email' with the correct key name
        shared_data2 = data.get('name', None)


        options = Options()
        options.add_argument("--headless")  # Headless mode
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--blink-settings=imagesEnabled=false") 
       

        # Initialize the WebDriver
        driver = webdriver.Chrome(options=options)

        # Load a page that redirects
        url = "https://kyrusagency.freshdesk.com/support/login?type=bot"  
        driver.get(url)

        cookies = driver.get_cookies()

        # Filter and print the specific cookies
        extracted_cookies = {}
        for cookie in cookies:
            if cookie['name'] in ['_helpkit_session', 'session_token','user_credentials','session_state']:
                extracted_cookies[cookie['name']] = cookie['value']
        driver.delete_all_cookies()

        driver.quit()

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
    pass
