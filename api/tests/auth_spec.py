#!/usr/bin/env python3

import pytest
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token, decode_token
from datetime import timedelta
import time

from api import create_app, db
from api.v1.views import auth_views
from api.models.models import User, Organisation

@pytest.fixture(scope='module')
def flask_app():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        app.register_blueprint(auth_views)
        yield app


@pytest.fixture(scope='module')
def client(flask_app):
    app = flask_app
    ctx = flask_app.test_request_context()
    ctx.push()
    app.test_client_class = FlaskClient
    return app.test_client()

def test_user_reg(client):
    '''Ensure a user is registered successfully when no organisation details are provided.
    Verify the default organisation name is correctly generated
    Check that the response contains the expected user details and access token
    '''
    res = client.post('/auth/register', json={
            'firstName': 'Andy',
            'lastName': 'Jane',
            'email': 'andy@example.com',
            'password': 'password',
            'phone': '0987654321'
        })
    assert res.status_code == 201
    assert 'accessToken' in res.json['data']
    assert 'Andy' in res.json['data']['user']['firstName']
    assert 'andy@example.com' in res.json['data']['user']['email']

    usr = User.query.filter_by(first_name = 'Andy').first()
    assert usr is not None

    org = Organisation.query.filter_by(name = "Andy's Organisation").first()
    assert org is not None

def test_successful_login(client):
    res = client.post('/auth/login', json={
            'email': 'andy@example.com',
            'password': 'password'
        })
    assert res.status_code == 200
    assert 'accessToken' in res.json['data']
    assert 'andy@example.com' in res.json['data']['user']['email']
    
def test_invalid_login_credentials(client):
    res = client.post('/auth/login', json={
            'email': 'andy@example.com',
            'password': 'passrd'
        })
    assert res.status_code == 401

def test_missing_required_lastName(client):
    res = client.post('/auth/register', json={
            'firstName': 'John',
            'email': 'john@example.com',
            'password': 'password',
            'phone': '0987654321'
        })
    print(res.get_json())
    assert res.status_code == 422
    err_msg = {"field": "lastName", "message": "lastName is required"}
    assert err_msg in res.json['errors']

def test_missing_required_firstName(client):
    res = client.post('/auth/register', json={
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password',
            'phone': '0987654321'
        })
    assert res.status_code == 422
    err_msg = {"field": "firstName", "message": "firstName is required"}
    assert err_msg in res.json['errors']

def test_missing_required_pwd(client):
    res = client.post('/auth/register', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'phone': '0987654321'
        })
    assert res.status_code == 422
    err_msg = {"field": "password", "message": "password is required"}
    assert err_msg in res.json['errors']

def test_missing_required_email(client):
    res = client.post('/auth/register', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'password': 'password',
            'phone': '0987654321'
        })
    assert res.status_code == 422
    err_msg = {"field": "email", "message": "email is required"}
    assert err_msg in res.json['errors']

def test_duplicate_email(client):
    res = client.post('/auth/register', json={
            'firstName': 'John',
            'lastName': 'Dave',
            'email': 'andy@example.com',
            'password': 'password',
            'phone': '0987654321'
        })
    assert res.status_code == 422
    err_msg = {"field": "email", "message": "Email already exists"}
    assert err_msg in res.json['errors']

def test_token_expiration(client):
    response = client.post('/auth/login', json={
            'email': 'andy@example.com',
            'password': 'password'
        })

    data = response.get_json()
    access_token = data['data']['accessToken']
    decoded_token = decode_token(access_token)

    user_id = decoded_token.get('sub')
    usr = User.query.filter_by(id=user_id).first()
    assert usr is not None

    # Verify token expiration
    expiration_time = decoded_token['exp']
    current_time = time.time()
    assert expiration_time <= current_time + 3600
