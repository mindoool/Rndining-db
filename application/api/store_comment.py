# -*- coding: utf-8 -*-
from flask import request, jsonify
from . import api
from application import db
from application.models.store_comment import StoreComment
from application.models.store import Store
from application.models.user import User
from application.models.mixin import SerializableModelMixin
from application.lib.rest.auth_helper import required_token, required_admin


# create, content, user_id, board_id
@api.route('/stores/<int:store_id>/store-comments', methods=['POST'])
@required_token
def create_store_comments(store_id, request_user_id=None):
    request_params = request.get_json()
    content = request_params.get('content')
    request_params['storeId'] = store_id
    request_params['userId'] = request_user_id

    if content is None:
        return jsonify(
            userMessage="내용을 입력해주세요."
        ), 400

    if store_id is None:
        return jsonify(
            userMessage="댓글을 작성할 식당을 입력해주세요."
        ), 400

    try:
        store = db.session.query(Store).filter(Store.id == store_id).one()
    except:
        return jsonify(
            userMessage="댓글 작성할 식단날짜를 잘못 선택하셨습니다."
        )

    if request_user_id is None:
        return jsonify(
            userMessage="유저 정보가 없습니다."
        ), 400

    try:
        store_comment = StoreComment()
        store_comment = store_comment.update_data(**request_params)
        db.session.add(store_comment)
        db.session.commit()

        q = db.session.query(StoreComment, User) \
            .outerjoin(User, User.id == StoreComment.user_id) \
            .filter(StoreComment.id == store_comment.id)

        return jsonify(
            data=SerializableModelMixin.serialize_row(q.one())
        ), 200
    except:
        return jsonify(
            userMessage="server deny your request, check param value"
        ), 403


# read
@api.route('/stores/<int:store_id>/store-comments/<int:store_comment_id>', methods=['GET'])
@required_token
def get_store_comment_by_id(store_id, store_comment_id, request_user_id=None):
    store_comment = db.session.query(StoreComment, User) \
        .outerjoin(User, User.id == StoreComment.user_id) \
        .filter(StoreComment.id == store_comment_id)

    if store_comment is None:
        return jsonify(
            userMessage="댓글을 찾을 수 없습니다."
        ), 400

    return jsonify(
        data=SerializableModelMixin.serialize_row(store_comment.one())
    ), 200


# read
@api.route('/stores/<int:store_id>/store-comments', methods=['GET'])
@required_token
def get_store_comments(store_id, request_user_id=None):
    last_id = request.args.get('lastId')
    limit = request.args.get('limit', default=15)

    store_comments = db.session.query(StoreComment, User) \
        .outerjoin(User, User.id == StoreComment.user_id) \
        .filter(StoreComment.store_id == store_id) \
        .order_by(StoreComment.id.desc())

    if last_id is not None:
        store_comments = store_comments.filter(StoreComment.id < last_id)

    if int(limit) > 15:
        limit = 15

    store_comments = store_comments.limit(limit)

    return jsonify(
        data=map(SerializableModelMixin.serialize_row, store_comments)
    ), 200


# update
@api.route('/stores/<int:store_id>/store-comments/<int:store_comment_id>', methods=['PUT'])
@required_token
def update_store_comment_by_id(store_id, store_comment_id, request_user_id=None):
    request_params = request.get_json()
    content = request_params.get('content')
    store_comment = db.session.query(StoreComment).get(store_comment_id)

    if store_comment.user_id != request_user_id:
        return jsonify(
            userMessage="댓글은 본인만 수정 가능합니다."
        )

    if store_comment is None:
        return jsonify(
            userMessage="댓글을 찾을 수 없습니다."
        ), 400
    else:
        store_comment.content = content

    db.session.commit()
    return get_store_comment_by_id(store_id, store_comment_id)


# delete
@api.route('/stores/<int:store_id>/store-comments/<int:store_comment_id>', methods=['DELETE'])
@required_token
def delete_store_comment_by_id(store_id, store_comment_id, request_user_id=None):
    store_comment = db.session.query(StoreComment).get(store_comment_id)

    if store_comment.user_id != request_user_id:
        return jsonify(
            userMessage="댓글은 본인만 삭제 가능합니다."
        ), 401

    if store_comment is None:
        return jsonify(
            userMessage="댓글을 찾을 수 없습니다."
        ), 400
    else:
        try:
            db.session.delete(store_comment)
            db.session.commit()
            return jsonify(
                userMessage="삭제가 완료되었습니다."
            ), 200
        except:
            return jsonify(
                userMessage="오류가 발생했습니다. 관리자에 문의하세요."
            ), 403
