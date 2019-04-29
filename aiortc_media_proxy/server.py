import asyncio
import os

import aiohttp
from aiohttp import web
from aiohttp_validate import validate
import aiohttp_cors

from aiortc_media_proxy.stream import StreamPool
from aiortc_media_proxy.log import log

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


async def handle_admin_panel(request):
    log.debug('Get admin view')
    content = open(os.path.join(BASE_DIR, 'static/admin.html'), 'r').read()
    return web.Response(content_type='text/html', text=content)


@validate(
    request_schema={
        "type": "object",
        "properties": {
            "uri": {"type": "string"},
            "options": {
                "type": "object",
                "properties": {
                    "rtsp_transport": {"type": ["string", "null"]},
                    "timeout": {"type": ["integer", "null"]},
                    "width": {"type": ["integer", "null"]},
                }
            }
        },
        "required": ["uri"],
        "additionalProperties": False
    }
)
async def handle_stream_creation(params, request):
    uri = params['uri']

    log.debug(f'Create new stream {uri}')

    stream = await request.app['stream_pool'].create_stream(uri, params['options'])

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

    stream.ws_add(ws)

    if not stream.is_started():
        await stream.start()

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
        stream.ws_remove(ws)

    return ws


async def on_startup(app):
    asyncio.create_task(app['stream_pool'].cleanup_task())


def init():
    log.info('Init application')

    app = web.Application()
    app['stream_pool'] = StreamPool()

    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    app.router.add_get('/', handle_admin_panel)
    cors.add(app.router.add_post('/stream', handle_stream_creation))
    app.router.add_get('/stream', handle_stream_list)
    cors.add(app.router.add_get('/ws/{key}', handle_ws))
    app.router.add_static('/static', os.path.join(BASE_DIR, 'static'), name='static')

    app.on_startup.append(on_startup)

    web.run_app(app, port=80)
