# coding: utf8
from inspect import getargspec
from functools import wraps
from traceback import print_exc
from flask import jsonify
from flask import request
from application import db
from application.models.user import User
from application.lib.jwt.jwt_helper import jwt_decode


def get_user_from_request():
    """

    :param request:
    :return: sqlalchemy user query reusult object
    """
    token_string = request.headers.get('Authorization')
    decoded_data = jwt_decode(token_string)
    user_id = decoded_data.get("user_id")
    return db.session.query(User).get(user_id)


def required_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            token_string = request.headers.get('Authorization')
        except:
            print_exc()
            return jsonify(
                userMessage="Authorization required"
            ), 401

        try:
            decoded_data = jwt_decode(token_string)
        except:
            print_exc()
            return jsonify(
                userMessage="invalid token",
                errorCode="1"
            ), 401

        decoded_user_id = decoded_data.get("user_id")
        if 'request_user_id' in getargspec(f).args:
            kwargs['request_user_id'] = decoded_user_id

        return f(*args, **kwargs)

    return decorated_function


def required_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user_from_request()
        if user is None or not user.is_admin:
            return jsonify(
                userMessage="this request, admin authorization need"
            ), 401

        return f(*args, **kwargs)

    return decorated_function
