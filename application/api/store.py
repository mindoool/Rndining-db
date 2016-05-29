# -*- coding: utf-8 -*-
from flask import request, jsonify
from . import api
from application import db
from application.models.store import Store
from application.models.mixin import SerializableModelMixin
from application.lib.rest.auth_helper import required_token, required_admin


@api.route('/stores', methods=['POST'])
# @required_token
def create_stores():
    """
    ms
    :param request_user_id:
    :return:
    """
    request_params = request.get_json()
    name = request_params.get('name')
    category = request_params.get('category')

    # day가 제대로 입력이 안된 경우
    if name is None:
        return jsonify(
            userMessage="가게 이름을 기입해주세요."
        ), 400

    # category가 제대로 입력이 안된 경우
    if category is None:
        return jsonify(
            userMessage="카테고리 정보를 기입해주세요."
        ), 400

    # 이미 등록되어있는지 확인
    q = db.session.query(Store).filter(Store.name == name, Store.category == category)
    if q.count() > 0:
        return jsonify(
            userMessage="이미 기입되어 있는 내용입니다."
        ), 409

    try:
        for key in request_params.keys():
            request_params[SerializableModelMixin.to_snakecase(key)] = request_params.pop(key)

        store = Store(**request_params)
        db.session.add(store)
        db.session.commit()

        return jsonify(
            data=store.serialize()
        ), 200
    except:
        return jsonify(
            userMessage="오류가 발생했습니다. 관리자에게 문의해주세요."
        ), 403


# read 개별
@api.route('/stores/<int:store_id>', methods=['GET'])
@required_token
def get_store_by_id(store_id):
    """
    ms
    :param store_id:
    :return:
    """
    try:
        store = db.session.query(Store).get(store_id)
        return jsonify(
            data=store.serialize()
        ), 200

    except:
        return jsonify(
            userMessage="해당 가게를 찾을 수 없습니다."
        ), 404


# read 복수
@api.route('/stores', methods=['GET'])
@required_token
def get_stores():
    """
    ms
    :return: request_user_id
    """
    q = db.session.query(Store)

    name = request.args.get('name')
    category = request.args.get('category')

    if name is not None:
        q = q.filter(Store.name == name)

    if category is not None:
        q = q.filter(Store.category == category)

    return jsonify(
        data=map(lambda obj: obj.serialize(), q)
    ), 200


# update
@api.route('/stores/<int:store_id>', methods=['PUT'])
@required_token
def update_store(store_id):
    """
    :param store_id:
    :return:
    """
    store = db.session.query(Store).get(store_id)

    if store is None:
        return jsonify(
            userMessage="가게를 찾을 수 없습니다."
        ), 404

    request_params = request.get_json()
    name = request_params.get('name')
    category = request_params.get('category')

    if category is not None and category not in ['korean', 'western', 'soup', 'meet']:
        return jsonify(
            userMessage="'한식', '양식', '찌개', '고기' 중 선택해주세요."
        ), 403

    store = store.update_data(**request_params)
    db.session.commit()

    return get_store_by_id(store_id)


# delete 필요없을듯하당
@api.route('/stores/<int:store_id>', methods=['DELETE'])
@required_admin
def delete_store(store_id):
    try:
        store = db.session.query(Store).get(store_id)

        try:
            db.session.delete(store)
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
            userMessage="가게를 찾을 수 없습니다."
        ), 404
