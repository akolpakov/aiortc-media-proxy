import os

from aiohttp import web


async def index(request):
    # content = open(os.path.join(ROOT, 'index.html'), 'r').read()
    # return web.Response(content_type='text/html', text=content)
    return web.Response(text='Hello world!')


app = web.Application()
# app.on_shutdown.append(on_shutdown)
app.router.add_get('/', index)
# app.router.add_get('/client.js', javascript)
# app.router.add_post('/offer', offer)
web.run_app(app, port=80)
