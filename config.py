import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'super_secret_key'
JWT_EXPIRATION_DELTA = timedelta(seconds=900)

