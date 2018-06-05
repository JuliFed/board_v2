from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object('config')
app.debug = True
database = SQLAlchemy(app)

db = database
bcrypt = Bcrypt(app)