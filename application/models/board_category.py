# -*- coding: utf-8 -*-
from application import db
from application.models.mixin import TimeStampMixin
from application.models.mixin import SerializableModelMixin


class BoardCategory(db.Model, TimeStampMixin, SerializableModelMixin):
    """
        전체공지게시판, 체어게시판, 지료실에 쓰일 카테고리
        어드민만 작성
    """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    is_notice = db.Column(db.Boolean, default=False)  # 공지인지 아닌지
    is_chair = db.Column(db.Boolean, default=False)  # notice일 때 체어공지인지 아닌지
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=[user_id])
