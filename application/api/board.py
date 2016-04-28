# -*- coding: utf-8 -*-
from flask import request, jsonify
from sqlalchemy import or_
from . import api
from application import db
from application.models.board import Board
from application.models.user import User
from application.models.mixin import SerializableModelMixin
from application.lib.rest.auth_helper import required_token
from application.lib.rest.auth_helper import required_admin


# create, title, content, only_chair, board_category_id, semester_id
@api.route('/boards', methods=['POST'])
@required_token
def create_boards(request_user_id=None):
    request_params = request.get_json()
    title = request_params.get('title')
    content = request_params.get('content')
    request_params['userId'] = request_user_id
    is_notice = request_params.get('isNotice')
    user = db.session.query(User).get(request_user_id)

    if title is None:
        return jsonify(
            userMessage="제목을 입력해주세요."
        ), 400

    if content is None:
        return jsonify(
            userMessage="내용을 입력해주세요."
        ), 400

    if is_notice == True:
        if user.is_admin == 0:
            return jsonify(
                userMessage="공지사항은 관리자만 작성할 수 있습니다."
            )

    try:
        board = Board()
        board = board.update_data(**request_params)

        db.session.add(board)
        db.session.commit()

        q = db.session.query(Board, User).outerjoin(User, User.id == Board.user_id).filter(Board.id == board.id)

        return jsonify(
            data=SerializableModelMixin.serialize_row(q.one())
        ), 200
    except Exception as e:
        print e.message
        return jsonify(
            userMessage="오류가 발생했습니다. 관리자에게 문의해주세요."
        ), 403


# read
@api.route('/boards/<int:board_id>', methods=['GET'])
@required_token
def get_board_by_id(board_id, request_user_id=None):
    try:
        q = db.session.query(Board, User).outerjoin(User, User.id == Board.user_id).filter(Board.id == board.id)
        return jsonify(
            data=SerializableModelMixin.serialize_row(q.one())
        ), 200
    except:
        return jsonify(
            userMessage="게시물을 찾을 수 없습니다."
        ), 404


# read
@api.route('/boards', methods=['GET'])
@required_token
def get_boards(request_user_id=None):
    last_id = request.args.get('lastId')
    limit = request.args.get('limit', default=15)
    keyword = request.args.get('keyword')
    is_notice = (request.args.get('isNotice', 'false').lower() == 'true')
    user = db.session.query(User).get(request_user_id)

    q = db.session.query(Board, User).outerjoin(User, User.id == Board.user_id)

    if last_id is not None:
        q = q.filter(Board.id < int(last_id))

    if is_notice:
        q = q.filter(Board.is_notice == 1)
    else:
        q = q.filter(Board.is_notice == 0)

    if keyword is not None:
        q = q.filter(Board.content.like(keyword + '%'))

    if int(limit) > 15:
        limit = 15

    q = q.order_by(Board.id.desc()).limit(limit)

    return jsonify(
        data=map(SerializableModelMixin.serialize_row, q)
    ), 200


# 검색 하는거 필요 full index search in sqlalchemy
# update
@api.route('/boards/<int:board_id>', methods=['PUT'])
@required_admin
@required_token
def update_boards(board_id, request_user_id=None):
    try:
        q = db.session.query(Board, User).outerjoin(User, User.id == Board.user_id).filter(Board.id == board_id)
        if q is not None:
            (board, user) = q.one()
    except:
        return jsonify(
            userMessage="게시물을 찾을 수 없습니다."
        ), 404

    user = db.session.query(User).get(request_user_id)
    if user is None:
        return jsonify(
            userMessage="유저 정보를 찾을 수 없습니다."
        )

    if board.user_id != user.id:
        return jsonify(
            userMessage="본인만 수정할 수 있습니다."
        )

    request_params = request.get_json()

    board = board.update_data(**request_params)
    db.session.commit()

    return jsonify(
        data=SerializableModelMixin.serialize_row(q.one())
    )


# delete
@api.route('/boards/<int:board_id>', methods=['DELETE'])
@required_token
def delete_board(board_id, request_user_id=None):
    try:
        board = db.session.query(Board).get(board_id)
        user = db.session.query(User).get(request_user_id)
        try:
            if board.is_notice == 1:
                if user.is_admin == 0:
                    return jsonify(
                        userMessage="공지사항은 관리자만 삭제할 수 있습니다."
                    )
            else:
                if board.user_id != request_user_id:
                    return jsonify(
                        userMessage="본인만 삭제할 수 있습니다."
                    )
            db.session.delete(board)
            db.session.commit()
            return jsonify(
                userMessage="삭제가 완료되었습니다."
            ), 200
        except:
            return jsonify(
                userMessage="오류가 발생했습니다. 관리자에 문의해주세요."
            ), 403

    except:
        return jsonify(
            userMessage="게시판 글을 찾을 수 없습니다."
        ), 404
