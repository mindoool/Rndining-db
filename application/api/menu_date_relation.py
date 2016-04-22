# -*- coding: utf-8 -*-
import datetime
from flask import request, jsonify
from . import api
from application import db
from application.models.menu_date_relation import MenuDateRelation
from application.models.meal_date import MealDate
from application.models.menu import Menu
from application.api.meal_date import create_meal_dates
from application.models.mixin import SerializableModelMixin
from application.lib.rest.auth_helper import required_token, required_admin


@api.route('/menu-date-relations', methods=['POST'])
@required_token
def create_meal_date_relations():
    request_params = request.get_json()
    meal_id = request_params.get('mealId')
    date = request_params.get('date').split('-')
    date_object = datetime.date(int(date[0]), int(date[1]), int(date[2]))
    menus = request_params.get('menus')

    # 'rice', 'soup', 'maindish', 'sidedish', 'bread', 'drink', 'fruit', 'noodle', 'salad'
    # rice = request_params.get('rice')
    # soup = request_params.get('soup')
    # maindish = request_params.get('maindish')
    # sidedish = request_params.get('sidedish')
    # bread = request_params.get('bread')
    # drink = request_params.get('drink')
    # fruit = request_params.get('fruit')
    # noodle = request_params.get('noodle')
    # salad = request_params.get('salad')

    # date, meal_id가 제대로 입력이 안된 경우
    if date is None:
        return jsonify(
            userMessage="날짜를 입력해주세요."
        ), 400
    elif meal_id is None:
        return jsonify(
            userMessage="식단을 입력해주세요."
        )
    else:
        meal_date = db.session.query(MealDate).filter(MealDate.date == date_object, MealDate.meal_id == meal_id)
        if meal_date.count() > 0:
            meal_date_id = meal_date.id
        else:
            meal_date = MealDate(date=date_object, meal_id=meal_id)
            db.session.add(meal_date)
            db.session.commit()
            meal_date_id = meal_date.id

    # menus가 제대로 입력이 안된 경우
    menu_id_list = []
    if menus is None:
        return jsonify(
            userMessage="메뉴를 입력해주세요."
        )
    else:
        for key in menus.keys():
            menu = db.session.query(Menu).filter(Menu.name == menus[key])
            if menu.count() > 0:
                menu_id_list.append(menu.id)
            else:
                menu = Menu(name=menus[key], category=key)
                db.session.add(menu)
                db.session.commit()
                menu_id_list.append(menu.id)

    # 이미 등록되어있는지 확인
    menu_date_relation_list = []
    for menu_id in menu_id_list:
        q = db.session.query(MenuDateRelation).filter(MenuDateRelation.menu_id == menu_id,
                                                      MenuDateRelation.meal_date_id == meal_date_id)
        if q.count() > 0:
            return jsonify(
                userMessage="이미 등록되어있는 관계입니다."
            ), 409

        try:
            menu_date_relation = MenuDateRelation(menu_id=menu_id, meal_date_id=meal_date_id)
            db.session.add(menu_date_relation)
            db.session.commit()
            menu_date_relation_list.append(menu_date_relation.serialize())
        except:
            return jsonify(
                userMessage="오류가 발생했습니다. 관리자에게 문의해주세요."
            ), 403

    return jsonify(
            data=menu_date_relation_list
        ), 200


# read 개별
@api.route('/menu-date-relations/<int:menu_date_relation_id>', methods=['GET'])
@required_token
def get_menu_date_relation_by_id(menu_date_relation_id):
    try:
        menu_date_relation = db.session.query(MenuDateRelation).get(menu_date_relation_id)
        q = db.session.query(MenuDateRelation, Menu, MealDate) \
            .outerjoin(Menu.id == MenuDateRelation.menu_id) \
            .outerjoin(MealDate.id == MenuDateRelation.meal_date_id)
        return jsonify(
            # data=menu_date_relation.serialize()
            data=map(SerializableModelMixin.serialize_row, q)
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
