from flask import Blueprint

api = Blueprint('api', __name__)

from . import (
    meal,
    meal_date,
    menu,
    user,
    menu_date_relation,
    comment,
    board,
    board_category,
    store,
    store_comment,
    menu_store_relation
)