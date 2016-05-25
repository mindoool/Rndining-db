# -*- coding: utf-8 -*-
from application import db
from application.models.mixin import TimeStampMixin
from application.models.mixin import SerializableModelMixin

class MenuStoreRelation(db.Model, TimeStampMixin, SerializableModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'))
    menu = db.relationship('Menu', foreign_keys=[menu_id])
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'))
    store = db.relationship('Store', foreign_keys=[store_id])
