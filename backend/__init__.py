from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from backend.config import Config
from werkzeug.routing import BaseConverter


class YearConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(YearConverter, self).__init__(url_map)
        self.regex = r'[-]?\d+'

    def to_python(self, value):
        return int(value)


app = Flask(__name__)
CORS(app)
login = LoginManager(app)
login.login_view = 'login'
app.config.from_object(Config)
app.url_map.converters['year'] = YearConverter


import backend.queries
import backend.database
import backend.help
