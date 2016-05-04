# -*- coding: utf-8 -*-
import datetime
from flask import request, jsonify
from . import api
from application import db
from application.models.menu_date_relation import MenuDateRelation
from application.models.meal import Meal
from application.models.meal_date import MealDate
from application.models.menu import Menu
from application.api.meal_date import create_meal_dates
from application.models.mixin import SerializableModelMixin
from application.lib.rest.auth_helper import required_token, required_admin


@api.route('/menu-date-relations', methods=['POST'])
# @required_token
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
        try:
            meal_date = db.session.query(MealDate).filter(MealDate.date == date_object, MealDate.meal_id == meal_id).one()
            meal_date_id = meal_date.id
        except:
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
            menu = db.session.query(Menu).filter(Menu.name == menus[key]).one()
            if menu:
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
            continue
            # return jsonify(
            #     userMessage="이미 등록되어있는 관계입니다."
            # ), 409

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
# @required_token
def get_menu_date_relation_by_id(menu_date_relation_id):
    try:
        q = db.session.query(MenuDateRelation, Menu, MealDate) \
            .outerjoin(Menu, Menu.id == MenuDateRelation.menu_id) \
            .outerjoin(MealDate, MealDate.id == MenuDateRelation.meal_date_id) \
            .filter(MenuDateRelation.id == menu_date_relation_id)
        return jsonify(
            data=SerializableModelMixin.serialize_row(q.one())
        ), 200

    except:
        return jsonify(
            userMessage="해당 관계를 찾을 수 없습니다."
        ), 404


# read
@api.route('/meal-date-menus', methods=['GET'])
# @required_token
def get_menu_dates():
    date = request.args.get('date')
    if date is not None:
        date = request.args.get('date').split('-')
        date_object = datetime.date(int(date[0]), int(date[1]), int(date[2]))
    else:
        date_object = datetime.date.today()

    q1 = db.session.query(MealDate, Meal).outerjoin(Meal, Meal.id == MealDate.meal_id) \
        .filter(MealDate.date == date_object)

    meal_dates = {}
    meal_date_ids = []
    for row in q1:
        (meal_date, meal) = row
        serialized_data = SerializableModelMixin.serialize_row(row)
        serialized_data['menus'] = []
        meal_dates[meal_date.id] = serialized_data
        meal_date_ids.append(meal_date.id)

    q2 = db.session.query(MenuDateRelation, Menu).outerjoin(Menu, Menu.id == MenuDateRelation.menu_id) \
        .filter(MenuDateRelation.meal_date_id.in_(meal_date_ids))
    for (menu_date_relation, menu) in q2:
        meal_dates[menu_date_relation.meal_date_id]['menus'].append(menu.serialize())

    return jsonify(
        data=meal_dates.values()
    ), 200


# update
@api.route('/menu-date-relations/<int:menu_date_relation_id>', methods=['PUT'])
# @required_token
def update_menu_date_relation(menu_date_relation_id):
    menu_date_relation = db.session.query(MenuDateRelation).filter(MenuDateRelation.id == menu_date_relation_id).one()

    if menu_date_relation is None:
        return jsonify(
            userMessage="관계를 찾을 수 없습니다."
        ), 404

    request_params = request.get_json()

    if request_params.get('menuId'):
        menu_id = request_params.get('menuId')
    else:
        menu_id = menu_date_relation.menu_id

    if request_params.get('mealDateId'):
        meal_date_id = request_params.get('mealDateId')
    else:
        meal_date_id = menu_date_relation.meal_date_id

    q = db.session.query(MenuDateRelation).filter(MenuDateRelation.menu_id == menu_id, MenuDateRelation.meal_date_id)
    if q.count() > 0:
        if q.one() == menu_date_relation:
            pass
        else:
            return jsonify(
                userMessage="기존에 동일한 관계가 있습니다."
            )
    else:
        menu_date_relation.menu_id = menu_id
        menu_date_relation.meal_date_id = meal_date_id
        db.session.commit()

    return get_menu_date_relation_by_id(menu_date_relation_id)


# delete 필요없을듯하당
@api.route('/menu-date-relations/<int:menu_date_relation_id>', methods=['DELETE'])
# @required_admin
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
