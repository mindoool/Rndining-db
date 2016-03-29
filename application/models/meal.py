# -*- coding: utf-8 -*-
from application import db
from application.models.mixin import TimeStampMixin
from application.models.mixin import SerializableModelMixin

class Meal(db.Model, TimeStampMixin, SerializableModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Enum('월요일', '화요일', '수요일', '목요일', '금요일'), nullable=False)
    time = db.Column(db.Enum('아침', '점심', '저녁'))
    category = db.Column(db.Enu,('라면', '샐러드', '간편식', '한식','양식', '석식', '석식-면'))