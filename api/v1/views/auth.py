#!/usr/bin/python3
'''
    RESTful API actions for auth actions
'''

from flask import jsonify, abort, request
from api import db
from api.models.models import User, Organisation
from flask_jwt_extended import create_access_token
from api.v1.views import auth_views


@auth_views.route('/register', methods=['POST'], strict_slashes=False)
def register():
    'Registers a user'
    payload = request.get_json()

    #validation
    errors = []
    for field in ['firstName', 'lastName', 'email', 'password']:
        if not payload.get(field):
            errors.append({"field": field, "message": f"{field} is required"})
        if not isinstance(payload.get(field), str) :
            errors.append({"field": field, "message": f"{field} must be a string"})
    if errors:
        return jsonify({"errors": errors}), 422

    #check if user is already registered
    email = payload.get("email")
    if User.query.filter_by(email = email).first() is not None:
        errors.append({"field": "email", "message": "Email already exists"})
        return jsonify({"errors": errors}), 422
    
    #register user & create Org
    #try:
    user = User(email = email)
    user.first_name = payload.get("firstName")
    user.last_name = payload.get("lastName")
    user.hash_password(payload.get("password"))
    user.phone = payload.get("phone")
    org_name = "{}'s Organisation".format(user.first_name)
    org = Organisation(name = org_name)
    user.orgs.append(org)

    # save user to db
    db.session.add(user)
    db.session.add(org)
    db.session.commit()

    # create access_token
    access_token = create_access_token(identity=user.id)
    """     except Exception:
        return jsonify({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "statusCode": 400
        }), 400 """

    return jsonify({
        'status': 'success',
        "message": "Registration successful",
        "data": {
            "accessToken": access_token,
            "user": {
                "userId": user.id,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
                "phone": user.phone
            }
        }
    }), 201


@auth_views.route('/login', methods=['POST'], strict_slashes=False)
def login():
    'logs in a user'
    data = request.get_json()

    if "email" not in data or "password" not in data:
        return jsonify({
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
    }), 401

    user = User.query.filter_by(email=data.get('email')).first()
    if user and user.verify_password(data.get('password')):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "data": {
                "accessToken": access_token,
                "user": {
                    "userId": user.id,
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "email": user.email,
                    "phone": user.phone
                }
            }
        }), 200

    return jsonify({
        "status": "Bad request",
        "message": "Authentication failed",
        "statusCode": 401
    }), 401
