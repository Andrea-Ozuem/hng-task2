#!/usr/bin/python3
'''
    RESTful API actions for app endpoints
'''
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, request
from api import db
from api.models.models import User, Organisation
from api.v1.views import app_views


@app_views.route('/users/<user_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_userRec(user_id):
    '''a user gets their own record or user record in organisations they belong to 
    or created [PROTECTED]'''
    jwt_id = get_jwt_identity()
    current_user = User.query.get(jwt_id)
    if current_user.id == user_id:
        return jsonify({
            "status": "success",
            "message": "User record retrieved successfully",
            "data": {
                "userId": current_user.id,
                "firstName": current_user.first_name,
                "lastName": current_user.last_name,
                "email": current_user.email,
                "phone": current_user.phone
            }
        }), 200

    # get record if common organisation
    all_user_ids = list()
    for orgs in list(current_user.orgs):
        for usr in list(orgs.users):
            all_user_ids.append(usr.id)
    if user_id in all_user_ids:
        usr_withId = User.query.get(user_id)
        return jsonify({
            "status": "success",
            "message": "User record retrieved successfully",
            "data": {
                "userId": usr_withId.id,
                "firstName": usr_withId.first_name,
                "lastName": usr_withId.last_name,
                "email": usr_withId.email,
                "phone": usr_withId.phone
            }
        }), 200
        
    return jsonify({
        "status": "Bad Request",
        "message": "Resource protected",
        "statusCode": 403
    }), 403


@app_views.route('/organisations', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_userOrg():
    '''gets all your organisations the user belongs to or created.'''
    jwt_id = get_jwt_identity()
    current_user = User.query.get(jwt_id)

    if not current_user:
        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 404
    orgs = list(current_user.orgs)
    return jsonify({
        "status": "success",
        "message": "Organisations retrieved successfully",
        "data": {
            "organisations": [{
                "orgId": org.id,
                "name": org.name,
                "description": org.description
            } for org in orgs]
        }
    }), 200


@app_views.route('/organisations/<org_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_orgRec(org_id):
    '''gets all your organisations the user belongs to or created.'''
    jwt_id = get_jwt_identity()
    current_user = User.query.get(jwt_id)
    if not current_user:
        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 404

    org = Organisation.query.get(org_id)
    if not org or org not in current_user.orgs:
        return jsonify({
            "status": "error",
            "message": "Organisation not found or access denied"
        }), 404
    return jsonify({
        "status": "success",
        "message": "Organisation retrieved successfully",
        "data": {
            "orgId": org.id,
            "name": org.name,
            "description": org.description
        }
    }), 200

@app_views.route('/organisations', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_org():
    '''
    a user can create their new organisation [PROTECTED].
    Request body: 
    {
	    "name": "string", // Required and cannot be null
	    "description": "string",
    }
    '''
    jwt_id = get_jwt_identity()
    current_user = User.query.get(jwt_id)
    data = request.get_json()

    # validation
    errors = []
    name = data.get('name')
    desc = data.get('description')
    if not name:
        errors.append({"field": "name", "message": "name is required"})
    if not isinstance(name, str):
        errors.append({"field": "name", "message": "name must be a string"})
    if desc and (not isinstance(name, str)):
        errors.append({"field": "description", "message": "description must be a string"})
    if errors:
        return jsonify({"errors": errors}), 422

    try:
        org = Organisation(name=name, description=desc)
        current_user.orgs.append(org)
        db.session.add(org)
        db.session.commit()
    except Exception:
        return jsonify(
            {
                "status": "Bad Request",
                "message": "Client error",
                "statusCode": 400
            }), 400
    return jsonify(
        {
            "status": "success",
            "message": "Organisation created successfully",
            "data": {
	            "orgId": org.id, 
				"name": org.name, 
				"description": org.description
            }
        }), 201


@app_views.route('/organisations/<orgId>/users', methods=['POST'], strict_slashes=False)
def add_user(orgId):
    ''' adds a user to a particular organisation
        Request body:
        {
            "userId": "string"
        }
    '''
    data = request.get_json()

    # validation
    errors = []
    u_id = data.get('userId')
    if not u_id:
        errors.append({"field": "userId", "message": "userId is required"})
    try:
        org = Organisation.query.get(orgId)
        user = User.query.get(u_id)
        if not user:
            return jsonify({
                "field": "userId",
                "message": "User does not exist",
                "statusCode": 400
            })
        org.users.append(user)
        db.session.commit()
    except Exception:
        return jsonify(
            {
                "status": "Bad Request",
                "message": "Client error",
                "statusCode": 400
            }), 400
    return jsonify({
        "status": "success",
        "message": "User added to organisation successfully",
    }), 200