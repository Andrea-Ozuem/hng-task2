#!/usr/bin/python3
""" initializes view of directory  """
from flask import Blueprint

app_views = Blueprint('app_views', __name__, url_prefix='/api')
auth_views = Blueprint('auth_views', __name__, url_prefix='/auth')

from api.v1.views.auth import *
from api.v1.views.users import *