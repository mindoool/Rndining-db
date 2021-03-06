# -*- coding: utf-8 -*-
from application import db
from application.models.mixin import TimeStampMixin
from application.models.mixin import SerializableModelMixin


class Comment(db.Model, TimeStampMixin, SerializableModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="cascade"))
    user = db.relationship('User', foreign_keys=[user_id])

    meal_date_id = db.Column(db.Integer, db.ForeignKey('meal_date.id', ondelete="cascade"))
    board = db.relationship('MealDate', foreign_keys=[meal_date_id])
