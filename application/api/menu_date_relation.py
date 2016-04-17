# -*- coding: utf-8 -*-
import datetime
from flask import request, jsonify
from . import api
from application import db
from application.models.menu_date_relation import MenuDateRelation
from application.models.mixin import SerializableModelMixin
from application.lib.rest.auth_helper import required_token, required_admin


@api.route('/menu-date-relations', methods=['POST'])
@required_token
def create_meal_date_relations():
    request_params = request.get_json()
    menu_id = request_params.get('menuId')
    meal_date_id = request_params.get('mealDateId')

    # meal_id가 제대로 입력이 안된 경우
    if menu_id is None:
        return jsonify(
            userMessage="식단 정보를 기입해주세요."
        ), 400

    # meal_date_id가 제대로 입력이 안된 경우
    if meal_date_id is None:
        return jsonify(
            userMessage="식단 날짜 정보를 기입해주세요."
        ), 400

    # 이미 등록되어있는지 확인
    q = db.session.query(MenuDateRelation).filter(MenuDateRelation.menu_id == menu_id,
                                                  MenuDateRelation.meal_date_id == meal_date_id)
    if q.count() > 0:
        return jsonify(
            userMessage="이미 등록되어있는 관계입니다."
        ), 409

    try:
        for key in request_params.keys():
            request_params[SerializableModelMixin.to_snakecase(key)] = request_params.pop(key)

        menu_date_relation = MenuDateRelation(**request_params)
        db.session.add(menu_date_relation)
        db.session.commit()

        return jsonify(
            data=menu_date_relation.serialize()
        ), 200
    except:
        return jsonify(
            userMessage="오류가 발생했습니다. 관리자에게 문의해주세요."
        ), 403


# read 개별
@api.route('/menu-date-relations/<int:menu_date_relation_id>', methods=['GET'])
@required_token
def get_menu_date_relation_by_id(menu_date_relation_id):
    try:
        menu_date_relation = db.session.query(MenuDateRelation).get(menu_date_relation_id)
        return jsonify(
            data=menu_date_relation.serialize()
        ), 200

    except:
        return jsonify(
            userMessage="해당 관계를 찾을 수 없습니다."
        ), 404


# read
@api.route('/menu-date-relations', methods=['GET'])
@required_token
def get_meal_dates():
    q = db.session.query(MenuDateRelation)

    menu_id = request.args.get('menuId')
    meal_date_id = request.args.get('mealDateId')

    if menu_id is not None:
        q = q.filter(MenuDateRelation.menu_id == menu_id)

    if meal_date_id is not None:
        q = q.filter(MenuDateRelation.meal_date_id == meal_date_id)

    return jsonify(
        data=map(lambda obj: obj.serialize(), q)
    ), 200


# update
@api.route('/menu-date-relations/<int:menu_date_relation_id>', methods=['PUT'])
@required_token
def update_menu_date_relation(menu_date_relation_id):
    menu_date_relation = db.session.query(MenuDateRelation).get(menu_date_relation_id)

    if menu_date_relation is None:
        return jsonify(
            userMessage="관계를 찾을 수 없습니다."
        ), 404

    request_params = request.get_json()
    menu_id = request_params.get('menuId')
    meal_date_id = request_params.get('mealDateId')

    if menu_id is not None:
        from sqlalchemy.exc import IntegrityError
        try:
            menu_date_relation.menu_id = menu_id
        except IntegrityError as e:
            return jsonify(
                userMessage="기존에 동일한 메뉴의 관계가 있습니다."
            )

    if meal_date_id is not None:
        from sqlalchemy.exc import IntegrityError
        try:
            menu_date_relation.meal_date_id = meal_date_id
        except IntegrityError as e:
            return jsonify(
                userMessage="기존에 동일한 날짜의 관게가 있습니다."
            )

    db.session.commit()

    return get_menu_date_relation_by_id(meal_date_id)


# delete 필요없을듯하당
@api.route('/menu-date-relations/<int:menu_date_relation_id>', methods=['DELETE'])
@required_admin
def delete_menu_date_relation(menu_date_relation_id):
    try:
        menu_date_relation = db.session.query(MenuDateRelation).get(menu_date_relation_id)

        try:
            db.session.delete(menu_date_relation)
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
            userMessage="해당 관계를 찾을 수 없습니다."
        ), 404