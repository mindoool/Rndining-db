# -*- coding: utf-8 -*-
from application import db
from application.models.mixin import TimeStampMixin
from application.models.mixin import SerializableModelMixin

class MenuDateRelation(db.Model, TimeStampMixin, SerializableModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'))
    menu = db.relationship('Menu', foreign_keys=[menu_id])
    meal_date_id = db.Column(db.Integer, db.ForeignKey('date.id'))
    meal_date = db.relationship('MealDate', foreign_keys=[meal_date_id])
