# -*- coding: utf-8 -*-
from peewee import *

from app import db


class BaseModel(Model):
    class Meta:
        database = db

    @classmethod
    def get_one(cls, *query, **kwargs):
        # 为了方便使用，新增此接口，查询不到返回None，而不抛出异常
        try:
            return cls.get(*query, **kwargs)
        except DoesNotExist:
            return None


class User(BaseModel):
    key = TextField(unique=True)
    priority = IntegerField()
    multiple = IntegerField()
    mark = TextField()


class Users(BaseModel):
    username = TextField(unique=True)
    password = TextField()
