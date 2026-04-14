import json
import os
import webbrowser
from flask import Flask, request
from kiteconnect import KiteConnect
from config.settings import API_KEY, API_SECRET

TOKEN_FILE = "config/token.json"

app = Flask(__name__)
kite = KiteConnect(api_key=API_KEY)

access_token_global = None


def save_token(access_token):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"access_token": access_token}, f)


def load_token():
    if not os.path.exists(TOKEN_FILE):
        return None

    with open(TOKEN_FILE, "r") as f:
        data = json.load(f)
        return data.get("access_token")


def generate_access_token(request_token):
    global access_token_global

    data = kite.generate_session(request_token, api_secret=API_SECRET)
    access_token = data["access_token"]

    save_token(access_token)
    access_token_global = access_token

    return access_token


@app.route("/")
def login_callback():
    global access_token_global

    request_token = request.args.get("request_token")

    if request_token:
        print("\nRequest token received!")
        generate_access_token(request_token)
        return "Login successful! You can close this tab."

    return "No request token found."

def auto_login():
    global access_token_global

    login_url = kite.login_url()

    print("\nLogin URL:")
    print(login_url)

    print("\nOpening browser for login...")
    webbrowser.open(login_url)

    app.run(port=5000)

    return access_token_global