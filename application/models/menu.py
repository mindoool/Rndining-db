# -*- coding: utf-8 -*-
from application import db
from application.models.mixin import TimeStampMixin
from application.models.mixin import SerializableModelMixin


class Menu(db.Model, TimeStampMixin, SerializableModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.String(100))
    like_count = db.Column(db.Integer, default=0)
    category = db.Column(
        db.Enum('rice', 'soup', 'porridge', 'maindish', 'sidedish', 'bread', 'drink', 'fruit', 'noodle', 'salad', 'tea'))
