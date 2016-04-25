# -*- coding: utf-8 -*-
from application import db
from application.models.mixin import TimeStampMixin
from application.models.mixin import SerializableModelMixin
# from application.models.image import Image
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
    is_deleted = db.Column(db.Boolean, default=False)
    # is_activated = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<User %r>' % self.id

    def get_token(self):
        return jwt_encode({
            "email": self.email,
            "user_id": self.id,
            "is_admin": self.is_admin
        })

    @classmethod
    def image_and_password_process(cls, request_body):
        """
        image, password p
        :param request_body:
        :return:
        """

        # if 'image' in request_body:
        #     image_string_based64_encoded = request_body.pop('image')
        #     image = Image.add(image_string_based64_encoded, folder="image")
        #     request_body['profile_serving_url'] = image.serving_url

        if 'password' in request_body:
            print request_body
            request_body['password'] = password_encode(request_body.get('password'))

        return request_body

    def update_data(self, **kwargs):
        # pre operation before
        kwargs = User.image_and_password_process(kwargs)
        # check constraint
        return super(User, self).update_data(**kwargs)
