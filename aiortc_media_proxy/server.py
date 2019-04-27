import asyncio
import os

import aiohttp
from aiohttp import web
from aiohttp_validate import validate

from aiortc_media_proxy.stream import StreamPool
from aiortc_media_proxy.utils.log import log

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


async def handle_admin_panel(request):
    log.debug('Get admin view')
    content = open(os.path.join(BASE_DIR, 'static/admin.html'), 'r').read()
    return web.Response(content_type='text/html', text=content)


@validate(
    request_schema={
        "type": "object",
        "properties": {
            "url": {"type": "string"},
        },
        "required": ["url"],
        "additionalProperties": False
    }
)
async def handle_stream_creation(params, request):
    url = params['url']

    log.debug(f'Create new stream {url}')

    stream = await request.app['stream_pool'].create_stream(url)

    return web.json_response(stream.get_json_object())


async def handle_stream_list(request, *args):
    log.debug(f'Get stream list')

    streams = await request.app['stream_pool'].get_streams()

    return web.json_response({
        'streams': [stream.get_json_object() for stream in streams.values()]
    })


async def handle_ws(request):
    key = request.match_info['key']
    stream = request.app['stream_pool'].streams[key]

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    log.info(f'Create websocket {key}')

    sender_task = asyncio.create_task(stream.start(ws))

    try:
        async for msg in ws:
            if msg.tp == aiohttp.MsgType.text:
                log.info(msg.data)
            elif msg.tp == aiohttp.MsgType.closed:
                break
            elif msg.tp == aiohttp.MsgType.error:
                break
    finally:
        log.info(f'Close websocket {key}')
        sender_task.cancel()

    return ws


async def on_startup(app):
    asyncio.create_task(app['stream_pool'].cleanup_task())


def init():
    log.info('Init application')

    app = web.Application()
    app['stream_pool'] = StreamPool()

    app.router.add_get('/', handle_admin_panel)
    app.router.add_post('/stream', handle_stream_creation)
    app.router.add_get('/stream', handle_stream_list)
    app.router.add_get('/ws/{key}', handle_ws)
    app.router.add_static('/static', os.path.join(BASE_DIR, 'static'), name='static')

    app.on_startup.append(on_startup)

    web.run_app(app, port=80)
