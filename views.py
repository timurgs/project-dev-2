from aiohttp import web
from aiohttp_auth import auth

from models import Advertisement, User
from serializers import AdvertisementSerializer, UserSerializer
from app import app
from config import SALT
import hashlib


class AdvertisementView(web.View):

    async def get(self):
        adv_id = self.request.match_info['adv_id']
        adv = await Advertisement.get(int(adv_id))
        adv_data = adv.to_dict()
        return web.json_response(adv_data)

    async def post(self):
        adv_data = await self.request.json()
        adv_serialized = AdvertisementSerializer(**adv_data)
        adv_data = adv_serialized.dict()
        new_adv = await Advertisement.create_instance(**adv_data)
        return web.json_response(new_adv.to_dict())


class UserView(web.View):

    async def get(self):
        user_id = self.request.match_info['adv_id']
        user = await User.get(int(user_id))
        user_data = user.to_dict()
        return web.json_response(user_data)

    async def post(self):
        user_data = await self.request.json()
        user_serialized = UserSerializer(**user_data)
        user_data = user_serialized.dict()
        new_user = await User.create_instance(**user_data)
        return web.json_response(new_user.to_dict())


class LoginView(web.View):

    async def post(self):
        # user_remember = await auth.get_auth(self.request)
        # if user_remember is None:
        data = await self.request.post()
        username = data.get('username')
        email = data.get('email')
        raw_password = f'{data.get("password")}{SALT}'
        password = hashlib.md5(raw_password.encode()).hexdigest()
        user = await User.load(username=username, email=email, password=password).query.gino.first()
        print(user)
        if user:
            await auth.remember(self.request, user)
            return web.json_response({'status': 200, "message": "You are logged in"})
        else:
            return web.json_response({"status": 401,
                                      "message": "Username or Password Error"})
        # else:
        #     return web.json_response({"status": 200,
        #                               "message": "You are already logged in"})


app.add_routes([web.get('/advertisements/{adv_id:\d+}', AdvertisementView)])
app.add_routes([web.post('/advertisements', AdvertisementView)])
app.add_routes([web.get('/users/{user_id:\d+}', UserView)])
app.add_routes([web.post('/users', UserView)])
app.add_routes([web.post('/login', LoginView)])

web.run_app(app, host='0.0.0.0', port=8080)
