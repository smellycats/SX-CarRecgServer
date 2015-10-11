# -*- coding: utf-8 -*-
import os
import Queue
import random
from functools import wraps

import arrow
from flask import g, request
from flask_restful import reqparse, Resource
from passlib.hash import sha256_crypt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from car_recg import app, db, api, auth, limiter, logger, access_logger
from models import Users, Scope
import helper


def verify_addr(f):
    """IP地址白名单"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not app.config['WHITE_LIST_OPEN'] or request.remote_addr == '127.0.0.1' or request.remote_addr in app.config['WHITE_LIST']:
            pass
        else:
            return {'status': '403.6',
                    'message': u'禁止访问:客户端的 IP 地址被拒绝'}, 403
        return f(*args, **kwargs)
    return decorated_function


@auth.verify_password
def verify_password(username, password):
    if username.lower() == 'admin':
        user = Users.query.filter_by(username='admin').first()
    else:
        return False
    if user:
        return sha256_crypt.verify(password, user.password)
    return False


def verify_token(f):
    """token验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Access-Token'):
            return {'status': '401.6', 'message': 'missing token header'}, 401
        token_result = verify_auth_token(request.headers['Access-Token'],
                                         app.config['SECRET_KEY'])
        if not token_result:
            return {'status': '401.7', 'message': 'invalid token'}, 401
        elif token_result == 'expired':
            return {'status': '401.8', 'message': 'token expired'}, 401
        g.uid = token_result['uid']
        g.scope = set(token_result['scope'])

        return f(*args, **kwargs)
    return decorated_function


def verify_scope(scope):
    def scope(f):
        """权限范围验证装饰器"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'all' in g.scope or scope in g.scope:
                return f(*args, **kwargs)
            else:
                return {}, 405
        return decorated_function
    return scope


class Index(Resource):

    def get(self):
        return {
            'user_url': '%suser{/user_id}' % (request.url_root),
            'scope_url': '%suser/scope' % (request.url_root),
            'token_url': '%stoken' % (request.url_root),
            'recg_url': '%sv1/recg' % (request.url_root),
            'uploadrecg_url': '%sv1/uploadrecg' % (request.url_root),
            'state_url': '%sv1/state' % (request.url_root)
        }, 200, {'Cache-Control': 'public, max-age=60, s-maxage=60'}


class RecgListApiV1(Resource):

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('imgurl', type=unicode, required=True,
                            help='A jpg url is require', location='json')
        parser.add_argument('coord', type=list, required=True,
                            help='A coordinates array is require',
                            location='json')
        args = parser.parse_args()

        # 回调用的消息队列
        que = Queue.Queue()

        if app.config['RECGQUE'].qsize() > app.config['MAXSIZE']:
            return {'message': 'Server Is Busy'}, 449

        imgname = '%32x' % random.getrandbits(128)
        imgpath = os.path.join(app.config['IMG_PATH'], '%s.jpg' % imgname)
        try:
            helper.get_url_img(request.json['imgurl'], imgpath)
        except Exception as e:
            logger.error('Error url: %s' % request.json['imgurl'])
            return {'message': 'URL Error'}, 400

        app.config['RECGQUE'].put((10, request.json, que, imgpath))

        try:
            recginfo = que.get(timeout=15)

            os.remove(imgpath)
        except Queue.Empty:
            return {'message': 'Timeout'}, 408
        except Exception as e:
            logger.error(e)
        else:
            return {
                'imgurl': request.json['imgurl'],
                'coord': request.json['coord'],
                'recginfo': recginfo
            }, 201


class StateListApiV1(Resource):

    def get(self):
        return {
            'threads': app.config['THREADS'],
            'qsize': app.config['RECGQUE'].qsize()
        }


class UploadRecgListApiV1(Resource):

    def post(self):
        # 文件夹路径 string
        filepath = os.path.join(app.config['UPLOAD_PATH'],
                                arrow.now().format('YYYYMMDD'))
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        try:
            # 上传文件命名 随机32位16进制字符 string
            imgname = '%32x' % random.getrandbits(128)
            # 文件绝对路径 string
            imgpath = os.path.join(filepath, '%s.jpg' % imgname)
            f = request.files['file']
            f.save(imgpath)
        except Exception as e:
            logger.error(e)
            return {'message': 'File error'}, 400

        # 回调用的消息队列 object
        que = Queue.Queue()
        # 识别参数字典 dict
        r = {'coord': []}
        app.config['RECGQUE'].put((9, r, que, imgpath))
        try:
            recginfo = que.get(timeout=app.config['TIMEOUT'])
        except Queue.Empty:
            return {'message': 'Timeout'}, 408
        except Exception as e:
            logger.error(e)
        else:
            return {'coord': r['coord'], 'recginfo': recginfo}, 201

api.add_resource(Index, '/')
api.add_resource(RecgListApiV1, '/v1/recg')
api.add_resource(StateListApiV1, '/v1/state')
api.add_resource(UploadRecgListApiV1, '/v1/uploadrecg')
