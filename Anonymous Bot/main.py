from flask import Flask, Response, request
from asgiref.wsgi import WsgiToAsgi
import requests
from config import *
from telebot.types import Update
from bot import *

app = Flask(__name__)

@app.route("/api", methods=["POST"])
def api():
    data = request.json
    update = Update.de_json(data)
    if update.message:
        if update.message.text:
            if update.message.text.startswith("/"):
                command_handler(update.message)
            else:
                message_handler(update.message)
        else:
            message_handler(update.message)
    elif update.callback_query:
        inline_handler(update.callback_query)
    return Response("OK", status=200)

@app.route("/setwebhook")
def setwebhook():
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
        requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={URL}/api")
        return Response("Done", status=200)
    except Exception as e:
        return Response(str(e), status=500)

asgi_app = WsgiToAsgi(app)