# -*- coding: utf-8 -*-
from flask import request
from flask import jsonify
from . import api
from application import db
from application.models.board_category import BoardCategory
from application.models.user import User
from application.models.mixin import SerializableModelMixin
from application.lib.rest.auth_helper import required_token
from application.lib.rest.auth_helper import required_admin


@api.route('/board-categories', methods=['POST'])
@required_admin
def create_board_categories(request_user_id=None):
    """
    ms
    :return:
    """
    request_body = request.get_json()
    content = request_body.get('content')
    is_notice = request_body.get('isNotice')

    # content가 제대로 입력이 안된 경우
    if content is None:
        return jsonify(
            userMessage="게시판 구분을 기입해주세요."
        ), 400

    user = db.session.query(User).filter(User.id == request_user_id).first()
    if is_notice:
        if user.is_admin == 0:
            return jsonify(
                userMessage="공지사항은 어드민만 작성할 수 있습니다."
            )

    # 이미 등록되어있는지 확인
    q = db.session.query(BoardCategory).filter(BoardCategory.content == content)
    if q.count() > 0:
        return jsonify(
            userMessage="기존에 존재하는 게시판 메뉴명입니다."
        ), 409

    try:
        board_category = BoardCategory()
        board_category = board_category.update_data(**request_body)
        db.session.add(board_category)
        db.session.commit()

        return jsonify(
            data=board_category.serialize()
        ), 200
    except:
        return jsonify(
            userMessage="server deny your request, check param value"
        ), 403


# read 개별
@api.route('/board-categories/<int:board_category_id>', methods=['GET'])
@required_token
def get_board_category_by_id(board_category_id):
    """
    ms
    :param board_category_id:
    :return:
    """
    try:
        board_category = db.session.query(BoardCategory).get(board_category_id)
        return jsonify(
            data=board_category.serialize()
        ), 200

    except:
        return jsonify(
            userMessage="해당 게시판 메뉴를 찾을 수 없습니다."
        ), 404


# read
@api.route('/board-categories', methods=['GET'])
@required_token
def get_board_categories():
    """
    ms
    :return:
    """
    q = db.session.query(BoardCategory)

    return jsonify(
        data=map(lambda obj: obj.serialize(), q)
    ), 200


# update
@api.route('/board-categories/<int:board_category_id>', methods=['PUT'])
@required_admin
def update_board_category(board_category_id):
    """
    ms
    :param board_category_id:
    :return:
    """
    content = request.get_json().get('content')

    try:
        board_category = db.session.query(BoardCategory).get(board_category_id)
    except:
        return jsonify(
            userMessage="해당 게시판 메뉴를 찾을 수 없습니다."
        ), 404

    q = db.session.query(BoardCategory).filter(BoardCategory.content == content)
    if q.count() > 0:
        return jsonify(
            userMessage="이미 존재하는 게시판 메뉴명입니다."
        )

    board_category.content = content
    db.session.commit()

    return get_board_category_by_id(board_category.id)


# delete
@api.route('/board-categories/<int:board_category_id>', methods=['DELETE'])
@required_admin
def delete_board_category(board_category_id):
    """
    ms
    :param board_category_id:
    :return:
    """
    try:
        board_category = db.session.query(BoardCategory).get(board_category_id)
        try:
            db.session.delete(board_category)
            db.session.commit()
            return jsonify(
                userMessage="게시판 메뉴가 삭제되었습니다."
            ), 200
        except:
            return jsonify(
                userMessage="게시판 메뉴를 삭제할 수 없습니다."
            ), 403

    except:
        return jsonify(
            userMessage="해당 게시판 메뉴를 찾을 수 없습니다."
        ), 404
