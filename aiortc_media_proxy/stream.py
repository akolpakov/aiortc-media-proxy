import asyncio
import hashlib
from time import time

import ffmpeg

from aiortc_media_proxy.log import log


class Stream:
    TTL = 60    # TODO: dynamic
    time_up = 0

    ffmpeg_process = None

    def __init__(self, url):
        self.url = url
        self.key = self.get_key(url)
        self.up()

    @staticmethod
    def get_key(url):
        return hashlib.sha224(url.encode('utf-8')).hexdigest()

    @property
    def ttl(self):
        return max(self.TTL - int(time() - self.time_up), 0)

    def up(self):
        self.time_up = time()

    async def stream_to_client_task(self, ws):
        try:
            while True:
                frame = await self._read_ffmpeg_stream()

                if frame:
                    log.info(f'Send {self.key}: {len(frame)}')
                    await ws.send_bytes(frame)
                    await ws.drain()

                # HACK: https://github.com/aio-libs/aiohttp/issues/3391
                if ws._req.transport.is_closing():
                    log.info('Seems connection was interrupted')
                    break

                await asyncio.sleep(0.1)

        except Exception as error:
            log.error(error)
            await ws.close()

    async def start(self):
        args = (
            ffmpeg
                .input(self.url, fflags='nobuffer', flags='low_delay',)
                .filter('scale', 640, -1)   # TODO: dynamic
                .output('pipe:', format='mpegts', vcodec='mpeg1video')['v']
                .get_args()
        )

        self.ffmpeg_process = await asyncio.create_subprocess_exec('ffmpeg', *args, stdout=asyncio.subprocess.PIPE)

    async def stop(self):
        if self.ffmpeg_process:
            try:
                await self.ffmpeg_process.terminate()
            except ProcessLookupError:
                pass

    def get_json_object(self):
        return dict(
            url=self.url,
            key=self.key,
            ttl=self.ttl,
            ws=f'ws://127.0.0.1:8000/ws/{self.key}'     # TODO: dynamic
        )

    async def _read_ffmpeg_stream(self):
        if self.ffmpeg_process:
            in_bytes = await self.ffmpeg_process.stdout.read(1024*1024)
            if len(in_bytes) == 0:
                return None
            return in_bytes
        else:
            return None


class StreamPool:
    streams = dict()

    async def get_streams(self):
        return self.streams

    async def create_stream(self, url):
        key = Stream.get_key(url)

        if key not in self.streams:
            self.streams[key] = Stream(url)
            asyncio.create_task(self.streams[key].start())

        self.streams[key].up()

        return self.streams[key]

    async def cleanup_task(self):
        while True:

            log.debug('Run cleanup_task')

            # get expired streams

            to_remove = []
            for key, stream in self.streams.items():
                if stream.ttl <= 0:
                    await stream.stop()
                    to_remove.append(key)

            # remove streams

            for key in to_remove:
                del self.streams[key]

            await asyncio.sleep(10)
