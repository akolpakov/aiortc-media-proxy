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
        refresh_streams: async function() {
            const response = await this.$http.get('/stream');
            this.streams = response.data.streams;
        },
        create_stream: async function() {
            this.form.error = null;

            const data = {
                url: this.form.url
            };
            try {
                await this.$http.post('/stream', data);
                await this.refresh_streams()
            } catch(err) {
                this.form.error = err
            }
        },
        select_stream: async function(stream) {
            this.form.url = stream.url;
            await this.create_stream();
        }
    },
    created: async function () {
        await this.refresh_streams();
    }
});
