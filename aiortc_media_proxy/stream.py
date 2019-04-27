import asyncio
import hashlib
from time import time

from aiortc_media_proxy.utils.log import log
from .utils.singleton import Singleton


class Stream:
    TTL = 60
    time_up = 0

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

    async def start(self):
        # self.ffmpeg_process = (
        #     ffmpeg
        #         .input(self.stream_url, fflags='nobuffer', flags='low_delay',
        #                **self.ffmpeg_stream_args)  # , skip_frame='nokey'
        #         .output('pipe:', format='rawvideo', pix_fmt='rgb24')['v']
        #         .run_async(pipe_stdout=True, quiet=True)
        # )
        return self

    async def stop(self):
        pass

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

    async def close_expired_streams(self):
        while True:

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
