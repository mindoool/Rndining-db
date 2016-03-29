# -*- coding: utf-8 -*-
from application import db
from application.models.mixin import TimeStampMixin
from application.models.mixin import SerializableModelMixin
from application.lib.jwt.jwt_helper import jwt_encode
from application.lib.encript.encript_helper import password_encode


class User(db.Model, TimeStampMixin, SerializableModelMixin):
    __exclude_column_names__ = ('password',)

    # 기본정보
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200), nullable=False)
    nickname = db.Column(db.String(30), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    # is_activated = db.Column(db.Boolean, default=True)


    def __repr__(self):
        return '<User %r>' % self.id

    def get_token(self):
        return jwt_encode({
            "email": self.email,
            "user_id": self.id
        })

    @staticmethod
    def add(request_body):

        try:
            request_body['password'] = password_encode(request_body.get('password'))
            user = User(**request_body)
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            print e
            return None
