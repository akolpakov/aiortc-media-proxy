from aiortc import RTCSessionDescription, RTCPeerConnection
from aiortc.contrib.media import MediaPlayer

from aiortc_media_proxy.utils.log import log
from .utils.singleton import Singleton


class Stream:
    VIDEO_OPTIONS = dict(
        framerate='30',
        video_size='640x480'
    )

    def __init__(self, url, rtc_sdp, rtc_type):
        self.url = url
        self.rtc_sdp = rtc_sdp
        self.rtc_type = rtc_type
        self.pc = None

    async def init(self):
        self.pc = await self.__init()
        return self

    async def __init(self):

        # init RTC

        pc = RTCPeerConnection()

        @pc.on('iceconnectionstatechange')
        async def on_iceconnectionstatechange():
            log.info('ICE connection state is %s' % pc.iceConnectionState)

            if pc.iceConnectionState == 'failed':
                await pc.close()
                log.info('!!!!!!!!!!!')
                # self.pcs.discard(pc)

        # Init player

        player = MediaPlayer(self.url)

        # Add transceivers

        offer = RTCSessionDescription(sdp=self.rtc_sdp, type=self.rtc_type)
        await pc.setRemoteDescription(offer)

        for t in pc.getTransceivers():
            if t.kind == 'audio' and player.audio:
                pc.addTrack(player.audio)
            elif t.kind == 'video' and player.video:
                pc.addTrack(player.video)

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        return pc

    def get_js_object(self):
        return dict(
            url=self.url,
            sdp=self.pc.localDescription.sdp,
            type=self.pc.localDescription.type,
        )


class StreamPool(metaclass=Singleton):
    streams = dict()

    async def get_streams(self):
        return self.streams

    async def get_stream(self, url, rtc_sdp, rtc_type):
        # if url not in self.streams:
        #     self.streams[url] = await self.create_stream(url, rtc_sdp, rtc_type)
        # return self.streams[url]
        return await self.create_stream(url, rtc_sdp, rtc_type)

    async def create_stream(self, url, rtc_sdp, rtc_type):
        stream = Stream(url, rtc_sdp, rtc_type)
        return await stream.init()
