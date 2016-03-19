from flask import request, jsonify
from . import api
from application import db
from application.models.meal import Meal
from application.models.mixin import SerializableModelMixin
from application.lib.rest.auth_helper import required_token
from application.lib.rest.auth_helper import required_admin