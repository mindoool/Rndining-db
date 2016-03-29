# -*- coding: utf-8 -*-
from application import db
from application.models.mixin import TimeStampMixin
from application.models.mixin import SerializableModelMixin

class Menu(db.Model, TimeStampMixin, SerializableModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    menus = db.Column(db.String(1000))  # json [{"rice" : , "mainDish": ,},{},..., {}]