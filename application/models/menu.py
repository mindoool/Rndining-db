# -*- coding: utf-8 -*-
from application import db
from application.models.mixin import TimeStampMixin
from application.models.mixin import SerializableModelMixin

class Menu(db.Model, TimeStampMixin, SerializableModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    like_count = db.Column(db.Integer, default=0)
    category = db.Column(db.Enum('밥', '국', '메인반찬', '밑반찬', '빵', '음료', '과일','라면', '샐러드'))