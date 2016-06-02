# -*- coding: utf-8 -*-
import datetime
from flask import request, jsonify
from . import api
from application import db
from application.models.store_comment import StoreComment
from application.models.menu_store_relation import MenuStoreRelation
from application.models.store import Store
from application.models.meal import Meal
from application.models.meal_date import MealDate
from application.models.menu import Menu
from application.models.user import User
from application.models.mixin import SerializableModelMixin
from application.lib.rest.auth_helper import required_token, required_admin


@api.route('/menu-store-relations', methods=['POST'])
@required_token
def create_menu_store_relations():
    request_params = request.get_json()
    store_id = request_params.get('storeId')
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
    if store_id is None:
        return jsonify(
            userMessage="가게를 입력해주세요."
        )

    try:
        store = db.session.query(Store).filter(Store.id == store_id).one()
    except:
        return jsonify(
            userMessage="해당 가게가 존재하지 않습니다."
        )

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
    menu_store_relation_list = []
    for menu_id in menu_id_list:
        q = db.session.query(MenuStoreRelation).filter(MenuStoreRelation.menu_id == menu_id,
                                                      MenuStoreRelation.store_id == store_id)
        if q.count() > 0:
            continue
            # return jsonify(
            #     userMessage="이미 등록되어있는 관계입니다."
            # ), 409

        try:
            menu_store_relation = MenuStoreRelation(menu_id=menu_id, store_id=store_id)
            db.session.add(menu_store_relation)
            db.session.commit()
            menu_store_relation_list.append(menu_store_relation.serialize())
        except:
            return jsonify(
                userMessage="오류가 발생했습니다. 관리자에게 문의해주세요."
            ), 403

    return jsonify(
        data=menu_store_relation_list
    ), 200


# read 개별
@api.route('/menu-store-relations/<int:menu_store_relation_id>', methods=['GET'])
# @required_token
def get_menu_store_relation_by_id(menu_store_relation_id):
    try:
        q = db.session.query(MenuStoreRelation, Menu, Store) \
            .outerjoin(Menu, Menu.id == MenuStoreRelation.menu_id) \
            .outerjoin(Store, Store.id == MenuStoreRelation.store_id) \
            .filter(MenuStoreRelation.id == menu_store_relation_id)
        return jsonify(
            data=SerializableModelMixin.serialize_row(q.one())
        ), 200

    except:
        return jsonify(
            userMessage="해당 관계를 찾을 수 없습니다."
        ), 404


# read
@api.route('/menu-store-relations', methods=['GET'])
@required_token
def get_menu_stores():
    q1 = db.session.query(Store, StoreComment, User) \
        .outerjoin(StoreComment, StoreComment.store_id == MenuStoreRelation.store_id) \
        .outerjoin(User, User.id == StoreComment.user_id)

    name = request.args.get('name')
    if name is not None:
        q1 = q1.filter(Store.name.like('%' + name + '%'))

    stores = {}
    store_ids = []
    prev_store_id = None
    for row in q1:
        (store, store_comment, user) = row
        if prev_store_id != store.id:
            store_obj = store.serialize()
            store_obj['comments'] = []
            store_obj['menus'] = []
            stores[store.id] = store_obj
            store_ids.append(store.id)

        if store_comment is not None:
            store_comment_obj = store_comment.serialize()
            store_comment_obj['user'] = user.serialize()
            store_obj['comments'].append(store_comment_obj)

        prev_store_id = store.id

    q2 = db.session.query(MenuStoreRelation, Menu).outerjoin(Menu, Menu.id == MenuStoreRelation.menu_id) \
        .filter(MenuStoreRelation.store_id.in_(store_ids))
    for (menu_store_relation, menu) in q2:
        store[menu_store_relation.store_id]['menus'].append(menu.serialize())

    return jsonify(
        data=stores.values()
    ), 200


# update
# @api.route('/menu-date-relations/<int:menu_date_relation_id>', methods=['PUT'])
# # @required_token
# def update_menu_date_relation(menu_date_relation_id):
#     menu_date_relation = db.session.query(MenuDateRelation).filter(MenuDateRelation.id == menu_date_relation_id).one()
#
#     if menu_date_relation is None:
#         return jsonify(
#             userMessage="관계를 찾을 수 없습니다."
#         ), 404
#
#     request_params = request.get_json()
#
#     if request_params.get('menuId'):
#         menu_id = request_params.get('menuId')
#     else:
#         menu_id = menu_date_relation.menu_id
#
#     if request_params.get('mealDateId'):
#         meal_date_id = request_params.get('mealDateId')
#     else:
#         meal_date_id = menu_date_relation.meal_date_id
#
#     q = db.session.query(MenuDateRelation).filter(MenuDateRelation.menu_id == menu_id, MenuDateRelation.meal_date_id)
#     if q.count() > 0:
#         if q.one() == menu_date_relation:
#             pass
#         else:
#             return jsonify(
#                 userMessage="기존에 동일한 관계가 있습니다."
#             )
#     else:
#         menu_date_relation.menu_id = menu_id
#         menu_date_relation.meal_date_id = meal_date_id
#         db.session.commit()
#
#     return get_menu_date_relation_by_id(menu_date_relation_id)
#
#
# # delete 필요없을듯하당
# @api.route('/menu-date-relations/<int:menu_date_relation_id>', methods=['DELETE'])
# # @required_admin
# def delete_menu_date_relation(menu_date_relation_id):
#     try:
#         menu_date_relation = db.session.query(MenuDateRelation).get(menu_date_relation_id)
#
#         try:
#             db.session.delete(menu_date_relation)
#             db.session.commit()
#             return jsonify(
#                 userMessage="삭제가 완료되었습니다."
#             ), 200
#         except:
#             return jsonify(
#                 userMessage="삭제 실패."
#             ), 403
#
#     except:
#         return jsonify(
#             userMessage="해당 관계를 찾을 수 없습니다."
#         ), 404
