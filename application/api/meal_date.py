# -*- coding: utf-8 -*-
import datetime
from flask import request, jsonify
from . import api
from application import db
from application.models.meal_date import MealDate
from application.models.mixin import SerializableModelMixin
from application.lib.rest.auth_helper import required_token, required_admin


@api.route('/meal-dates', methods=['POST'])
@required_token
def create_meal_dates():
    request_params = request.get_json()
    date = request_params.get('date').split('-')
    date_object = datetime.date(int(date[0]), int(date[1]), int(date[2]))
    meal_id = request_params.get('mealId')

    # date가 제대로 입력이 안된 경우
    if date is None:
        return jsonify(
            userMessage="날짜를 기입해주세요."
        ), 400
    elif len(date) < 3:
        return jsonify(
            userMessage="날짜 형식이 잘못되었습니다. 날짜 입력을 다시 해주세요."
        ), 400

    if meal_id is None:
        return jsonify(
            userMessage="식단 정보를 기입해주세요."
        ), 400

    # 이미 등록되어있는지 확인
    q = db.session.query(MealDate).filter(MealDate.date == date_object, MealDate.meal_id == meal_id)
    if q.count() > 0:
        return jsonify(
            userMessage="이미 등록되어있는 식단 날짜입니다."
        ), 409

    try:
        for key in request_params.keys():
            request_params[SerializableModelMixin.to_snakecase(key)] = request_params.pop(key)

        meal_date = MealDate(**request_params)
        db.session.add(meal_date)
        db.session.commit()

        return jsonify(
            data=meal_date.serialize()
        ), 200
    except:
        return jsonify(
            userMessage="오류가 발생했습니다. 관리자에게 문의해주세요."
        ), 403