# -*- coding: utf-8 -*-
from application import db
from application.models.mixin import TimeStampMixin
from application.models.mixin import SerializableModelMixin

class Meal(db.Model, TimeStampMixin, SerializableModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    homework_id = db.Column(db.Integer, db.ForeignKey('homework.id'))
    homework = db.relationship('Homework', foreign_keys=[homework_id])