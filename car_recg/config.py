# -*- coding: utf-8 -*-
import Queue


class Config(object):
    # 密码 string
    SECRET_KEY = 'hellokitty'
    # 服务器名称 string
    HEADER_SERVER = 'SX-CarRecgServer'
    # 加密次数 int
    ROUNDS = 123456
    # token生存周期，默认1小时 int
    EXPIRES = 7200
    # 数据库连接 string
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../carrecgser.db'
    # 数据库连接绑定 dict
    SQLALCHEMY_BINDS = {}
    # 用户权限范围 dict
    SCOPE_USER = {}
    # 白名单启用 bool
    WHITE_LIST_OPEN = True
    # 白名单列表 set
    WHITE_LIST = set()
    # 处理线程数 int
    THREADS = 4
    # 允许最大数队列为线程数16倍 int
    MAXSIZE = THREADS * 16
    # 图片下载文件夹 string
    IMG_PATH = 'img'
    # 图片截取文件夹 string
    CROP_PATH = 'crop'
    # 超时 int
    TIMEOUT = 10
    # 识别优先队列 object
    RECGQUE = Queue.PriorityQueue()
    # 退出标记 bool
    IS_QUIT = False
    # 用户字典 dict
    USER = {}
    # 上传文件保存路径 string
    UPLOAD_PATH = 'upload'


class Develop(Config):
    DEBUG = True


class Production(Config):
    DEBUG = False


class Testing(Config):
    TESTING = True
