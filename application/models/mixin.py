# -*- coding: utf-8 -*-
import re
from json import dumps as json_dumps
from json import loads as json_loads
from calendar import timegm
from application import db


class TimeStampMixin(object):
    created_time = db.Column(db.TIMESTAMP,
                             default=db.func.utc_timestamp())
    modified_time = db.Column(db.TIMESTAMP,
                              default=db.func.utc_timestamp(),
                              onupdate=db.func.utc_timestamp())


class SerializableModelMixin(object):
    def serialize(self,
                  exclude_column_names=None,
                  extra_fields=None):

        if extra_fields is None:
            extra_fields = {}

        if exclude_column_names is None:
            if hasattr(self.__class__, '__exclude_column_names__'):
                exclude_column_names = self.__class__.__exclude_column_names__
            else:
                exclude_column_names = ()

        d = {}
        for column in self.__table__.columns:

            if column.name in exclude_column_names:
                d[SerializableModelMixin.to_camelcase(column.name)] = None
                continue

            value = getattr(self, column.name)

            if isinstance(column.type, db.Boolean) and value is None:
                value = False

            if value is None:
                d[SerializableModelMixin.to_camelcase(column.name)] = value
                continue

            # "YYYY-MM-DD", "YYYY-MM-DD:hh:mm:ss"형으로 그냥 넣으면
            # string 이 잘 박힘
            # 꺼내올때도 따로 파싱 필요없음
            if isinstance(column.type, db.TIMESTAMP):
                value = timegm(value.utctimetuple())
            elif isinstance(column.type, db.Date):
                value = value.isoformat()
            elif isinstance(column.type, db.DateTime):
                value = value.isoformat()
            else:
                pass

            if hasattr(self.__class__, '__json_column_names__'):
                if column.name in self.__class__.__json_column_names__ and \
                                type(value).__name__ in ['unicode', 'str']:
                    value = json_loads(value)

            d[SerializableModelMixin.to_camelcase(column.name)] = value

        d.update(extra_fields)

        return d

    def update_data(self, **kwargs):
        kwargs = SerializableModelMixin.dict_keys_camel_to_snake(kwargs)
        editable_column_list = self.get_editable_column_names()
        # if not set([key for key in kwargs]) <= set(editable_column_list):
        #     invalid_attr_str = str(set([key for key in kwargs]) - set(editable_column_list))
        #     raise AttributeError(
        #             'object has not update attr' + invalid_attr_str)

        for column_name in editable_column_list:
            if column_name not in kwargs:
                continue

            column = self.__table__.columns.get(column_name)
            value = kwargs.get(column_name)

            if isinstance(column.type, db.DateTime):
                pass
                # print value

            if value is not None and hasattr(self.__class__, '__json_column_names__'):
                if column.name in self.__class__.__json_column_names__:
                    value = json_dumps(value)

            if isinstance(column.type, db.Boolean):
                value = SerializableModelMixin.to_boolean_value(value)

            setattr(self, column_name, value)

        return self

    @classmethod
    def get_editable_column_names(cls):
        return map(lambda x: x.name, cls.__table__.columns)

    @classmethod
    def serialize_row(cls, joined_resource_tuple, main_resource_index=0):

        l = list(joined_resource_tuple)  # immutable to mutable l = [user, sem, team]
        main_resource = l.pop(main_resource_index)  # l = [ sem, team]
        d = main_resource.serialize()  # d = {user ..}

        # add key value of table name
        first_character_lowercase = lambda s: s[:1].lower() + s[1:] if s else ''
        table_names = map(first_character_lowercase, joined_resource_tuple._fields)
        print table_names

        for idx, item in enumerate(table_names):
            if idx != main_resource_index:
                d[item] = None

        for row in l:

            if row is None:
                continue

            if not hasattr(row, '__table__'):  # 테이블이 아니라 컬럼일 떄
                continue

            key = SerializableModelMixin.to_camelcase(row.__table__.name)
            d[key] = row.serialize() if row is not None else None


        return d

    @classmethod
    def dict_keys_camel_to_snake(cls, dic):
        for key in dic.keys():
            dic[SerializableModelMixin.to_snakecase(key)] = dic.pop(key)
        return dic

    @staticmethod
    def to_camelcase(s):
        return re.sub(r'(?!^)_([a-zA-Z])', lambda m: m.group(1).upper(), s)

    @staticmethod
    def to_snakecase(s):
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()

    @staticmethod
    def to_boolean_value(raw_argument):
        if type(raw_argument).__name__ == 'bool':
            return raw_argument

        if raw_argument is None:
            return None

        return raw_argument in [u'1', u'true', u'True', u't', u'T']
