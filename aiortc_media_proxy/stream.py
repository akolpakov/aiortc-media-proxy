import asyncio
import hashlib
from time import time

from aiortc_media_proxy.utils.log import log
from .utils.singleton import Singleton


class Stream:
    TTL = 60
    time_up = 0
    ws_task = None

    _test = 1

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
                log.info(f'Send {self.key}: {self._test}. {ws.closed}')

                await ws.send_str(f'{self.key}: {self._test}')
                await ws.drain()

                # HACK: https://github.com/aio-libs/aiohttp/issues/3391
                if ws._req.transport.is_closing():
                    log.info('Seems connection was interrupted')
                    break

                await asyncio.sleep(1)
                self._test += 1

        except Exception as error:
            await ws.close()

    async def start(self, ws):
        self.ws_task = asyncio.create_task(self.stream_to_client_task(ws))
        # self.ffmpeg_process = (
        #     ffmpeg
        #         .input(self.stream_url, fflags='nobuffer', flags='low_delay',
        #                **self.ffmpeg_stream_args)  # , skip_frame='nokey'
        #         .output('pipe:', format='rawvideo', pix_fmt='rgb24')['v']
        #         .run_async(pipe_stdout=True, quiet=True)
        # )
        return self

    async def stop(self):
        if self.ws_task:
            self.ws_task.cancel()

    def get_json_object(self):
        return dict(
            url=self.url,
            key=self.key,
            ttl=self.ttl,
        )


class StreamPool(metaclass=Singleton):
    streams = dict()

    async def get_streams(self):
        return self.streams

    async def create_stream(self, url):
        key = Stream.get_key(url)

        if key not in self.streams:
            self.streams[key] = Stream(url)

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
