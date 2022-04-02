import os
from flask import Flask, send_from_directory
from flask_cors import CORS
# from flask_httpauth import HTTPBasicAuth
# from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__,  static_folder='build')
# auth = HTTPBasicAuth()
CORS(app)

# users = {
#     "toc": generate_password_hash(os.environ.get("API_PWD"))
# }

# @auth.verify_password
# def verify_password(username, password):
#     if username in users and \
#             check_password_hash(users.get(username), password):
#         return username

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

from app.module.controllers.transcript import *
from app.module.controllers.table import *