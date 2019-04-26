const app = new Vue({
    el: '#app',
    data: {
        streams: [],
        form: {
            url: null,
            error: null,
        },
        pc: new RTCPeerConnection({
            sdpSemantics: 'unified-plan'
        }),
        stream: {
            audio: null,
            video: null,
        }
    },
    methods: {
        refresh_streams: function() {
            this.$http.get('/stream').then(response => {
                this.streams = response.data.streams;
            });
        },
        create_stream: function() {
            this.form.error = null;

            this.pc.createOffer().then(offer => {
                return this.pc.setLocalDescription(offer);
            }).then(() => {
                // wait for ICE gathering to complete
                return new Promise(resolve => {
                    if (this.pc.iceGatheringState === 'complete') {
                        resolve();
                    } else {
                        const checkState = () => {
                            console.info('Check state', this.pc.iceGatheringState);
                            if (this.pc.iceGatheringState === 'complete') {
                                this.pc.removeEventListener('icegatheringstatechange', checkState);
                                resolve();
                            }
                        };
                        this.pc.addEventListener('icegatheringstatechange', checkState);
                    }
                });
            }).then(() => {
                const offer = this.pc.localDescription;
                const data = {
                    url: this.form.url,
                    sdp: offer.sdp,
                    type: offer.type,
                };
                return this.$http.post('/stream', data);
            }).then(function(response) {
                return response.json();
            }).then(answer => {
                console.log(answer);
                return this.pc.setRemoteDescription({
                    sdp: answer.sdp,
                    type: answer.type,
                });
            }).then(() => {
                this.refresh_streams();
            }).catch(err => {
                console.error(err);
                this.form.error = err;
            });
        },
        select_stream: function(stream) {
            console.log(stream);
            this.form.url = stream.url;
            this.create_stream();
        }
    },
    created: function () {
        this.refresh_streams();

        this.pc.addTransceiver('video', {direction: 'recvonly'});
        this.pc.addTransceiver('audio', {direction: 'recvonly'});

        this.pc.addEventListener('track', evt => {
            console.log('TRACK!!', evt);
            if (evt.track.kind == 'video') {
                this.stream.video = evt.streams[0];     // it does not work
                document.getElementById('video').srcObject = evt.streams[0];
            } else {
                this.stream.audio = evt.streams[0];     // it does not work
                document.getElementById('audio').srcObject = evt.streams[0];
                // document.getElementById('audio').play();
            }
        });
    }
});
