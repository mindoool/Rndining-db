# -*- coding: utf-8 -*-
from flask import request, jsonify
from . import api
from application import db
from application.models.commnet import Comment
from application.models.meal_date import MealDate
from application.models.user import User
from application.models.menu import Menu
from application.models.mixin import SerializableModelMixin
from application.lib.rest.auth_helper import required_token, required_admin


# create, content, user_id, board_id
@api.route('/meal-dates/<int:meal_date_id>/comments', methods=['POST'])
@required_token
def create_comments(meal_date_id, request_user_id=None):
    request_params = request.get_json()
    content = request_params.get('content')
    request_params['mealDateId'] = meal_date_id
    request_params['userId'] = request_user_id

    if content is None:
        return jsonify(
            userMessage="내용을 입력해주세요."
        ), 400

    if meal_date_id is None:
        return jsonify(
            userMessage="댓글을 작성할 식단날짜를 입력해주세요."
        ), 400

    try:
        meal_date = db.session.query(MealDate).filter(MealDate.id == meal_date_id).one()
    except:
        return jsonify(
            userMessage="댓글 작성할 식단날짜를 잘못 선택하셨습니다."
        )

    if request_user_id is None:
        return jsonify(
            userMessage="유저 정보가 없습니다."
        ), 400

    try:
        comment = Comment()
        comment = comment.update_data(**request_params)
        db.session.add(comment)
        db.session.commit()

        q = db.session.query(Comment, User) \
            .outerjoin(User, User.id == Comment.user_id) \
            .filter(Comment.id == comment.id)

        return jsonify(
            data=SerializableModelMixin.serialize_row(q.one())
        ), 200
    except:
        return jsonify(
            userMessage="server deny your request, check param value"
        ), 403


# read
@api.route('/meal-dates/<int:meal_date_id>/comments/<int:comment_id>', methods=['GET'])
@required_token
def get_comment_by_id(meal_date_id, comment_id, request_user_id=None):
    comment = db.session.query(Comment, User) \
        .outerjoin(User, User.id == Comment.user_id) \
        .filter(Comment.id == comment_id)

    if comment is None:
        return jsonify(
            userMessage="댓글을 찾을 수 없습니다."
        ), 400

    return jsonify(
        data=SerializableModelMixin.serialize_row(comment.one())
    ), 200


# read
@api.route('/meal-dates/<int:meal_date_id>/comments', methods=['GET'])
@required_token
def get_comments(meal_date_id, request_user_id=None):
    last_id = request.args.get('lastId')
    limit = request.args.get('limit', default=15)

    comments = db.session.query(Comment, User) \
        .outerjoin(User, User.id == Comment.user_id) \
        .filter(Comment.meal_date_id == meal_date_id) \
        .order_by(Comment.id.desc())

    if last_id is not None:
        comments = comments.filter(Comment.id < last_id)

    if int(limit) > 15:
        limit = 15

    comments = comments.limit(limit)

    return jsonify(
        data=map(SerializableModelMixin.serialize_row, comments)
    ), 200


# update
@api.route('/meal-dates/<int:meal_date_id>/comments/<int:comment_id>', methods=['PUT'])
@required_token
def update_comment_by_id(meal_date_id, comment_id, request_user_id=None):
    request_params = request.get_json()
    content = request_params.get('content')
    comment = db.session.query(Comment).get(comment_id)

    if comment.user_id != request_user_id:
        return jsonify(
            userMessage="댓글은 본인만 수정 가능합니다."
        )

    if comment is None:
        return jsonify(
            userMessage="댓글을 찾을 수 없습니다."
        ), 400
    else:
        comment.content = content

    db.session.commit()
    return get_comment_by_id(meal_date_id, comment_id)


# delete
@api.route('/meal-dates/<int:meal_date_id>/comments/<int:comment_id>', methods=['DELETE'])
@required_token
def delete_comment_by_id(meal_date_id, comment_id, request_user_id=None):
    comment = db.session.query(Comment).get(comment_id)

    if comment.user_id != request_user_id:
        return jsonify(
            userMessage="댓글은 본인만 삭제 가능합니다."
        )

    if comment is None:
        return jsonify(
            userMessage="댓글을 찾을 수 없습니다."
        ), 400
    else:
        try:
            db.session.delete(comment)
            db.session.commit()
            return jsonify(
                userMessage="삭제가 완료되었습니다."
            ), 200
        except:
            return jsonify(
                userMessage="server error, try again"
            ), 403
