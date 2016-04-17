# -*- coding: utf-8 -*-
from flask import request, jsonify
from . import api
from application import db
from application.models.meal import Meal
from application.models.mixin import SerializableModelMixin
from application.lib.rest.auth_helper import required_token, required_admin


@api.route('/meals', methods=['POST'])
# @required_token
def create_meals():
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
    q = db.session.query(Meal).filter(Meal.day == day, Meal.time == time, Meal.category == category)
    if q.count() > 0:
        return jsonify(
            userMessage="이미 기입되어 있는 내용입니다."
        ), 409

    try:
        for key in request_params.keys():
            request_params[SerializableModelMixin.to_snakecase(key)] = request_params.pop(key)

        meal = Meal(**request_params)
        db.session.add(meal)
        db.session.commit()

        return jsonify(
            data=meal.serialize()
        ), 200
    except:
        return jsonify(
            userMessage="오류가 발생했습니다. 관리자에게 문의해주세요."
        ), 403


# read 개별
@api.route('/meals/<int:meal_id>', methods=['GET'])
@required_token
def get_meal_by_id(meal_id):
    """
    ms
    :param meal_id:
    :return:
    """
    try:
        meal = db.session.query(Meal).get(meal_id)
        return jsonify(
            data=meal.serialize()
        ), 200

    except:
        return jsonify(
            userMessage="해당 식단을 찾을 수 없습니다."
        ), 404


# read
@api.route('/meals', methods=['GET'])
@required_token
def get_meals():
    """
    ms
    :return: request_user_id
    """
    q = db.session.query(Meal)

    day = request.args.get('day')
    time = request.args.get('time')
    category = request.args.get('category')

    if day is not None:
        q = q.filter(Meal.day == day)

    if time is not None:
        q = q.filter(Meal.time == time)

    if category is not None:
        q = q.filter(Meal.category == category)

    return jsonify(
        data=map(lambda obj: obj.serialize(), q)
    ), 200


# update
@api.route('/meals/<int:meal_id>', methods=['PUT'])
@required_token
def update_meal(meal_id):
    """
    :param meal_id:
    :return:
    """
    meal = db.session.query(Meal).get(meal_id)

    if meal is None:
        return jsonify(
            userMessage="식단을 찾을 수 없습니다."
        ), 404

    request_params = request.get_json()
    day = request_params.get('day')
    time = request_params.get('time')
    category = request_params.get('category')

    if day not in ['mon', 'tue', 'wed', 'thu', 'fri']:
        return jsonify(
            userMessage="'월요일', '화요일', '수요일', '목요일', '금요일' 중 선택해주세요."
        ), 403

    if time not in ['morning', 'lunch', 'dinner']:
        return jsonify(
            userMessage="'아침', '점심', '저녁' 중 선택해주세요."
        ), 403

    if category not in ['noodle', 'salad', 'takeout', 'korean','western', 'dinner', 'dinner-noodle']:
        return jsonify(
            userMessage="'라면', '샐러드', '간편식', '한식','양식', '석식', '석식-면' 중 선택해주세요."
        ), 403

    meal = meal.update_data(**request_params)
    db.session.commit()

    return get_meal_by_id(meal_id)


# delete 필요없을듯하당
@api.route('/meals/<int:meal_id>', methods=['DELETE'])
@required_admin
def delete_meal(meal_id):
    try:
        meal = db.session.query(Meal).get(meal_id)

        try:
            db.session.delete(meal)
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
            userMessage="식단을 찾을 수 없습니다."
        ), 404