import jwt
from . import JWT_SECRET_KEY

def jwt_encode(data, expire_timestamp=None):
    if expire_timestamp is not None:
        data['exp'] = expire_timestamp
    return jwt.encode(data, JWT_SECRET_KEY, algorithm='HS512')


def jwt_decode(token):
    return jwt.decode(token, JWT_SECRET_KEY)
