#!/usr/bin/env python3

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    DB_USER = os.getenv('DB_USER')
    DB_PWD = os.getenv('DB_PWD')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{}:{}@aws-0-eu-central-1.pooler.supabase.com:6543/postgres".format(DB_USER, DB_PWD)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 3600,
    'connect_args': {'connect_timeout': 10}
    }

    app.config["JWT_SECRET_KEY"] = "super-secret"  # change using os.getenv!
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
    jwt = JWTManager(app)

    db.init_app(app)

    return app