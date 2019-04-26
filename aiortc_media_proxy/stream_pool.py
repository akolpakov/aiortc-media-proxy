from .utils.singleton import Singleton


class StreamPool(metaclass=Singleton):
    streams = dict()

    async def get_streams(self):
        return self.streams

    async def get_stream(self, url):
        if url not in self.streams:
            self.streams[url] = await self.create_stream(url)

        return self.streams[url]

    async def create_stream(self, url):
        return {'url': url}
