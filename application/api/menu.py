# -*- coding: utf-8 -*-
from flask import request, jsonify
from . import api
from application import db
from application.models.menu import Menu
from application.models.mixin import SerializableModelMixin
from application.lib.rest.auth_helper import required_token, required_admin


# create - name, category
@api.route('/menus', methods=['POST'])
# @required_token
def create_menus():
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


# read
@api.route('/menus/<int:menu_id>', methods=['GET'])
# @required_token
def get_menu_by_id(menu_id):
    try:
        menu = db.session.query(Menu).get(menu_id)
        return jsonify(
            data=menu.serialize()
        ), 200

    except:
        return jsonify(
            userMessage="해당 메뉴를 찾을 수 없습니다."
        ), 404


# read
@api.route('/menus', methods=['GET'])
# @required_token
def get_menus():
    q = db.session.query(Menu)

    name = request.args.get('name')
    category = request.args.get('category')

    if name is not None:
        q = q.filter(Menu.name == name)

    if category is not None:
        q = q.filter(Menu.category == category)

    return jsonify(
        data=map(lambda obj: obj.serialize(), q)
    ), 200


# update
@api.route('/menus/<int:menu_id>', methods=['PUT'])
# @required_token
def update_menu(menu_id):
    menu = db.session.query(Menu).filter(Menu.id == menu_id).one()

    if menu is None:
        return jsonify(
            userMessage="메뉴를 찾을 수 없습니다."
        ), 404

    request_params = request.get_json()
    if request_params.get('name'):
        name = request_params.get('name')
    else:
        name = menu.name

    if request_params.get('category'):
        category = request_params.get('category')
    else:
        category = menu.category

    q = db.session.query(Menu).filter(Menu.name == name, Menu.category == category)
    if q.count() > 0:
        if q.one() == menu:
            pass
        else:
            return jsonify(
                    userMessage="기존에 동일한 메뉴가 있습니다."
                )
    else:
        menu.name = name
        menu.category = category
        db.session.commit()

    return get_menu_by_id(menu_id)


# delete 필요없을듯하당
@api.route('/menus/<int:menu_id>', methods=['DELETE'])
# @required_admin
def delete_menu(menu_id):
    try:
        menu = db.session.query(Menu).get(menu_id)

        try:
            db.session.delete(menu)
            db.session.commit()
            return jsonify(
                userMessage="삭제가 완료되었습니다."
            ), 200
        except:
            return jsonify(
                userMessage="삭제 실패."
            ), 403

    except:
        return jsonify(
            userMessage="메뉴를 찾을 수 없습니다."
        ), 404