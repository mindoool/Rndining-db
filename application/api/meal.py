# -*- coding: utf-8 -*-
from flask import request, jsonify
from . import api
from application import db
from application.models.meal import Meal
from application.models.mixin import SerializableModelMixin
from application.lib.rest.auth_helper import required_token


@api.route('/meal', methods=['POST'])
@required_token
def create_meal(request_user_id=None):
    """
    ms
    :param request_user_id:
    :return:
    """
    request_params = request.get_json()
    day = request_params.get('day')
    time = request_params.get('time')
    category = request_params.get('category')

    # day가 제대로 입력이 안된 경우
    if day is None:
        return jsonify(
            userMessage="요일 정보를 기입해주세요."
        ), 400

    # time이 제대로 입력이 안된 경우
    if time is None:
        return jsonify(
            userMessage="시간 정보를 기입해주세요."
        ), 400

    # category가 제대로 입력이 안된 경우
    if category is None:
        return jsonify(
            userMessage="카테고리 정보를 기입해주세요."
        ), 400


    # 이미 등록되어있는지 확인
    q = db.session.query(AsIs).filter(AsIs.user_id == request_user_id, AsIs.content == content)
    if q.count() > 0:
        return jsonify(
            userMessage="이미 기입되어 있는 내용입니다."
        ), 409

    try:
        for key in request_params.keys():
            request_params[SerializableModelMixin.to_snakecase(key)] = request_params.pop(key)

        as_is = AsIs(**request_params)
        db.session.add(as_is)
        db.session.commit()

        return jsonify(
            data=as_is.serialize()
        ), 200
    except:
        return jsonify(
            userMessage="server deny your request, check param value"
        ), 403