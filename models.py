from aiohttp import web
import asyncpg

from app import db
from datetime import datetime
import config
import hashlib


class ModelMixin:

    @classmethod
    async def create_instance(cls, *args, **kwargs):
        try:
            return (await cls.create(*args, **kwargs))
        except asyncpg.exceptions.UniqueViolationError:
            raise web.HTTPBadRequest


class Advertisement(db.Model, ModelMixin):

    __tablename__ = 'advertisement'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text())
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    _idx1 = db.Index('app_advs_title', 'title')
    _idx2 = db.Index('app_advs_created_on', 'created_on')

    def __str__(self):
        return '<Adv {}, {}>'.format(self.title, self.description)

    def __repr__(self):
        return str(self)

    @classmethod
    async def create_instance(cls, *args, **kwargs):
        return (await super().create_instance(*args, **kwargs))

    def to_dict(self):
        adv_data = super().to_dict()
        adv_created_on = adv_data['created_on']
        adv_data['created_on'] = str(adv_created_on)
        adv_data['author'] = self.user.name
        return adv_data


class User(db.Model, ModelMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(17), nullable=False)
    name = db.Column(db.String(17), default='Anonim')
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(128), nullable=False)

    _idx1 = db.Index('app_users_username', 'username', unique=True)
    _idx2 = db.Index('app_users_name', 'name')
    _idx3 = db.Index('app_users_email', 'email', unique=True)

    def __str__(self):
        return '<User {}>'.format(self.username)

    def __repr__(self):
        return str(self)

    @classmethod
    async def create_instance(cls, *args, **kwargs):
        return (await super().create_instance(*args, **kwargs))

    def set_password(self, raw_password: str):
        raw_password = f'{raw_password}{config.SALT}'
        self.password = hashlib.md5(raw_password.encode()).hexdigest()

    def check_password(self, raw_password: str):
        raw_password = f'{raw_password}{config.SALT}'
        return self.password == hashlib.md5(raw_password.encode()).hexdigest()

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name
        }
