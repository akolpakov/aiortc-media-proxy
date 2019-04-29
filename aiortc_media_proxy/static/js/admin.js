const app = new Vue({
    el: '#app',
    data: {
        streams: [],
        form: {
            uri: null,
            options: {
                rtsp_transport: null,
                timeout: null,
                width: null,
            },
            error: null,
        },
        stream: null,
        jsmpeg: null,
        jsmpeReady: false,
    },
    methods: {
        refreshStreams: async function() {
            const response = await this.$http.get('/stream');
            this.streams = response.data.streams;
        },
        createStream: async function() {
            this.form.error = null;

            const data = {
                uri: this.form.uri,
                options: {
                    rtsp_transport: this.form.options.rtsp_transport,
                    timeout: parseInt(this.form.options.timeout),
                    width: parseInt(this.form.options.width),
                }
            };

            try {
                const response = await this.$http.post('/stream', data);
                this.stream = response.data;
                await this.showStream();
                await this.refreshStreams()
            } catch(err) {
                this.form.error = err
            }
        },
        selectStream: async function(stream) {
            this.form.uri = stream.uri;
            this.form.options = stream.options;
            await this.createStream();
        },
        getWSUrl: function(ws) {
            const url = window.location.href;
            const ws_url = url.replace(/(http)(s)?\:\/\//, "ws$2://");
            return ws_url.replace(/\/$/,"") + '/' + ws.replace(/^\//,"");
        },
        showStream: async function(stream) {
            const player_canvas = document.getElementById('player');
            this.jsmpeReady = false;

            if (this.jsmpeg) {
                this.jsmpeg.destroy();
            }

            this.jsmpeg = new JSMpeg.Player(this.getWSUrl(this.stream.ws), {
                autoplay: true,
                canvas: player_canvas,
                onPlay: () => {
                    this.jsmpeReady = true;
                }
            });

            player_canvas.style.maxWidth = '100%';
        },
    },
    created: async function () {
        await this.refreshStreams();
    }
});
