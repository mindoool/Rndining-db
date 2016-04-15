# -*- coding: utf-8 -*-
from flask import request, jsonify
from . import api
from application import db
from application.models.menu import Menu
from application.models.mixin import SerializableModelMixin
from application.lib.rest.auth_helper import required_token, required_admin


@api.route('/menus', methods=['POST'])
@required_token
def create_menus():
    """
    ms
    :param request_user_id:
    :return:
    """
    request_params = request.get_json()
    name = request_params.get('name')
    category = request_params.get('category')

    # name이 제대로 입력이 안된 경우
    if name is None:
        return jsonify(
            userMessage="메뉴명을 기입해주세요."
        ), 400

    # category가 제대로 입력이 안된 경우
    if category is None:
        return jsonify(
            userMessage="카테고리 정보를 기입해주세요."
        ), 400

    # 이미 등록되어있는지 확인
    q = db.session.query(Menu).filter(Menu.name == name, Menu.category == category)
    if q.count() > 0:
        return jsonify(
            userMessage="이미 등록되어있는 메뉴입니다."
        ), 409

    try:
        for key in request_params.keys():
            request_params[SerializableModelMixin.to_snakecase(key)] = request_params.pop(key)

        menu = Menu(**request_params)
        db.session.add(menu)
        db.session.commit()

        return jsonify(
            data=menu.serialize()
        ), 200
    except:
        return jsonify(
            userMessage="오류가 발생했습니다. 관리자에게 문의해주세요."
        ), 403