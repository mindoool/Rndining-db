# -*- coding: utf-8 -*-
from Crypto.Hash import SHA256

SALT = "asalkdfjWIDMf0KF"  # todo using os env var with appengine


def password_encode(password):
    hash = SHA256.new()
    hash.update(password)
    rtn_hash = hash.hexdigest()
    for i in range(0, 1004):
        hash.update(rtn_hash + SALT)
        rtn_hash = hash.hexdigest()
    return rtn_hash
