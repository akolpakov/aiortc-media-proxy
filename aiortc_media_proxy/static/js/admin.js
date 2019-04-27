const app = new Vue({
    el: '#app',
    data: {
        streams: [],
        form: {
            url: null,
            error: null,
        },
        webSocket: null,
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
                const stream = response.data;
                await this.createWebSocket(stream);
                await this.refreshStreams()
            } catch(err) {
                this.form.error = err
            }
        },
        selectStream: async function(stream) {
            this.form.url = stream.url;
            await this.createStream();
        },
        createWebSocket: async function(stream) {
            await this.closeWebSocket();

            this.webSocket = new WebSocket('ws://127.0.0.1:8000/ws/' + stream.key);

            this.webSocket.onopen = function (event) {
                console.log('Socket ' + stream.key + ' opened');
            };

            this.webSocket.onmessage = function (event) {
                console.log(event.data);
            };

            this.webSocket.onerror = function (event) {
                this.form.error = 'WebSocket unexpectedly closed'
            }
        },
        closeWebSocket: async function() {
            if (this.webSocket) {
                await this.webSocket.close();
                this.webSocket = null;
            }
        }
    },
    created: async function () {
        await this.refreshStreams();
    }
});
