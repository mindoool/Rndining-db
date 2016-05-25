# -*- coding: utf-8 -*-
from application import db
from application.models.mixin import TimeStampMixin
from application.models.mixin import SerializableModelMixin


class Meal(db.Model, TimeStampMixin, SerializableModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Enum('mon', 'tue', 'wed', 'thu', 'fri'), nullable=False)
    time = db.Column(db.Enum('morning', 'lunch', 'dinner'), nullable=False)
    category = db.Column(db.Enum('noodle', 'salad', 'takeout', 'korean', 'western', 'dinner', 'dinner-noodle'),
                         nullable=False)