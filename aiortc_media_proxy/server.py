import json
import os

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
            "sdp": {"type": "string"},
            "type": {"type": "string"},
        },
        "required": ["url", "sdp", "type"],
        "additionalProperties": False
    }
)
async def handle_stream_creation(request, *args):
    url = request['url']
    rtc_sdp = request['sdp']
    rtc_type = request['type']

    url = os.path.join(BASE_DIR, 'demo-instruct.wav')

    log.debug(f'Create new stream {url}')

    pool = StreamPool()
    stream = await pool.get_stream(url, rtc_sdp, rtc_type)

    return web.json_response(stream.get_js_object())


async def handle_stream_get_list(request, *args):
    log.debug(f'Get stream list')

    pool = StreamPool()
    streams = await pool.get_streams()

    return web.json_response({
        'streams': [stream.get_js_object() for stream in streams.values()]
    })


def init():
    log.info('Init application')

    app = web.Application()

    app.router.add_get('/', handle_admin_panel)
    app.router.add_post('/stream', handle_stream_creation)
    app.router.add_get('/stream', handle_stream_get_list)
    app.router.add_static('/static', os.path.join(BASE_DIR, 'static'), name='static')

    web.run_app(app, port=80)
