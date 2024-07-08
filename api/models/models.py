#!/usr/bin/python3
"""This module defines the Models for the API"""

from passlib.apps import custom_app_context as pwd_context
from api import db
import uuid


user_org = db.Table('users_organisations',
    db.Column('user_id', db.String, db.ForeignKey('users.id'), nullable=False, primary_key=True),
    db.Column('organisation_id', db.String, db.ForeignKey('organisations.id'), nullable=False, primary_key=True)
)

class User(db.Model):
    """This class defines a user by various attributes"""
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(32))
    orgs = db.relationship("Organisation", secondary=user_org, back_populates='users')

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

                
class Organisation(db.Model):
    """ Organistion class """
    __tablename__ = 'organisations'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(128))
    users = db.relationship('User', secondary=user_org, back_populates='orgs')