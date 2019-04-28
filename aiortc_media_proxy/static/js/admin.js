const app = new Vue({
    el: '#app',
    data: {
        streams: [],
        form: {
            url: null,
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
                url: this.form.url
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
            this.form.url = stream.url;
            await this.createStream();
        },
        showStream: async function(stream) {
            const player_canvas = document.getElementById('player');
            this.jsmpeReady = false;

            if (this.jsmpeg) {
                this.jsmpeg.destroy();
            }

            // player.style.display = "none";
            this.jsmpeg = new JSMpeg.Player(this.stream.ws, {
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
