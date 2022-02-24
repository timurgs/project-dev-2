from aiohttp import web
from aiohttp_auth import auth

from gino import Gino
import config
import pydantic


@web.middleware
async def validation_error_handler(request, handler):
    try:
        response = await handler(request)
    except pydantic.error_wrappers.ValidationError as er:
        response = web.json_response({'error': str(er)}, status=400)
    except AttributeError as ae:
        response = web.json_response({'error': str(ae)}, status=404)
    return response


app = web.Application(middlewares=[validation_error_handler])
db = Gino()


async def init_orm(app):
    print('Приложение стартовало')
    await db.set_bind(config.DB_DSN)
    await db.gino.create_all()
    yield
    await db.pop_bind().close()
    print('Приложение остановилось')


app.cleanup_ctx.append(init_orm)
