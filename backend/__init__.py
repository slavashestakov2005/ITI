from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_moment import Moment
from backend.config import Config


app = Flask(__name__)
CORS(app)
login = LoginManager(app)
login.login_view = 'login'
moment = Moment(app)
app.config.from_object(Config)


import backend.queries
import backend.database
import backend.help
import backend.eljur
import backend.excel
import backend.api
