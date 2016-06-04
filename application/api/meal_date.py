# -*- coding: utf-8 -*-
import datetime
from flask import request, jsonify
from . import api
from application import db
from application.models.meal_date import MealDate
from application.models.meal import Meal
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


# read 개별
@api.route('/meal-dates/<int:meal_date_id>', methods=['GET'])
@required_token
def get_meal_date_by_id(meal_date_id):
    try:
        meal_date = db.session.query(MealDate, Meal) \
            .join(Meal, Meal.id == MealDate.meal_id) \
            .filter(MealDate.id == meal_date_id)
        return jsonify(
            data=SerializableModelMixin.serialize_row(meal_date.one())
        ), 200

    except:
        return jsonify(
            userMessage="해당 식단 날짜를 찾을 수 없습니다."
        ), 404


# read
@api.route('/meal-dates', methods=['GET'])
@required_token
def get_meal_dates():
    q = db.session.query(MealDate, Meal) \
        .join(Meal, Meal.id == MealDate.meal_id)

    date = request.args.get('date')
    meal_id = request.args.get('mealId')

    if date is not None:
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        q = q.filter(MealDate.date == date)

    if meal_id is not None:
        q = q.filter(MealDate.meal_id == meal_id)

    return jsonify(
        # data=map(lambda obj: obj.serialize(), q)
        data=map(SerializableModelMixin.serialize_row, q)
    ), 200


# update
@api.route('/meal-dates/<int:meal_date_id>', methods=['PUT'])
@required_token
def update_meal_date(meal_date_id):
    meal_date = db.session.query(MealDate).filter(MealDate.id == meal_date_id).one()

    if meal_date is None:
        return jsonify(
            userMessage="식단 날짜를 찾을 수 없습니다."
        ), 404

    request_params = request.get_json()
    if request_params.get('date'):
        date = request_params.get('date').split('-')
        date_object = datetime.date(int(date[0]), int(date[1]), int(date[2]))
    else:
        date_object = meal_date.date

    if request_params.get('mealId'):
        meal_id = request_params.get('mealId')
    else:
        meal_id = meal_date.meal_id

    q = db.session.query(MealDate).filter(MealDate.meal_id == meal_id, MealDate.date == date_object)
    if q.count() > 0:
        if q.one() == meal_date:
            pass
        else:
            return jsonify(
                    userMessage="기존에 동일한 날짜의 식단이 있습니다."
                )
    else:
        meal_date.meal_id = meal_id
        meal_date.date = date_object
        db.session.commit()

    return get_meal_date_by_id(meal_date_id)


# delete 필요없을듯하당
@api.route('/meal-dates/<int:meal_date_id>', methods=['DELETE'])
@required_admin
def delete_meal_date(meal_date_id):
    try:
        meal_date = db.session.query(MealDate).get(meal_date_id)

        try:
            db.session.delete(meal_date)
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
            userMessage="식단 날짜를 찾을 수 없습니다."
        ), 404