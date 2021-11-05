import json
import os

from flask import Flask, redirect, url_for,request,abort,jsonify
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized

app = Flask(__name__)

app.secret_key = b"somerandomkeyforsigningcookies140" #needed for signing cookies
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "false"      
app.config["DISCORD_CLIENT_ID"] =  # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = ""                # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = "insert url here/callback" # URL to your callback endpoint.
AUTH_HEADER_NAME = "ertyjkjhgfdsdfgddfgfdgnbvcx" #random name (required)
AUTH_HEADER_VALUE = "awesrdtfyguikjhgfvdsfdgvhfdfvgfdgsg" #random value (required)
discord = DiscordOAuth2Session(app)
users = [] #ignore

@app.route("/")
def login():
    return discord.create_session(scope=["identify","guilds", "guilds.join"])
	

@app.route("/callback/")
def callback():
    discord.callback()
    return redirect(url_for(".me"))


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("login"))

def get_db():
    with open("users.json",) as f:
        return json.load(f)
def set_db(data):
    users.append(data)
    with open("users.json","w") as f:
        json.dump({"data":users},f,indent=4)
@app.route("/thankyou")
@requires_authorization
def me():
    user = discord.fetch_user()
    id = user.id
    info = discord.get_authorization_token()
    data = get_db()
    if not str(id) in str(data):
        set_db({id:info})
    return f"User id: {id}"
@app.route("/users") 
def showtext():
    if AUTH_HEADER_NAME in request.headers:
        if request.headers[AUTH_HEADER_NAME] == AUTH_HEADER_VALUE:
            return get_db()
        else:
            abort(404)
    else:
        abort(404)
if __name__ == "__main__":
    app.run()