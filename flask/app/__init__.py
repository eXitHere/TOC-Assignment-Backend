import os
from flask import Flask
from flask_cors import CORS


project_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)

from app.module.controller import *