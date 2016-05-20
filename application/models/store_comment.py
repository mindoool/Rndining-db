# -*- coding: utf-8 -*-
from application import db
from application.models.mixin import TimeStampMixin
from application.models.mixin import SerializableModelMixin


class StoreComment(db.Model, TimeStampMixin, SerializableModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="cascade"))
    user = db.relationship('User', foreign_keys=[user_id])

    store_id = db.Column(db.Integer, db.ForeignKey('store.id', ondelete="cascade"))
    store = db.relationship('Store', foreign_keys=[store_id])