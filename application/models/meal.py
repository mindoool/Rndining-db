# -*- coding: utf-8 -*-
from application import db
from application.models.mixin import TimeStampMixin
from application.models.mixin import SerializableModelMixin


class Store(db.Model, TimeStampMixin, SerializableModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum('mon', 'tue', 'wed', 'thu', 'fri'), nullable=False)
    category = db.Column(db.Enum('korean', 'western', 'soup', 'meat'))
