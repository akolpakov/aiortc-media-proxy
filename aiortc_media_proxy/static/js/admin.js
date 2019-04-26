const app = new Vue({
    el: '#app',
    data: {
        streams: [],
        form: {
            url: null,
            error: null,
        }
    },
    methods: {
        refresh_streams: function() {
            this.$http.get('/stream').then(response => {
                this.streams = response.data.streams;
            });
        },
        create_stream: function(event) {
            this.form.error = null;
            const data = {
                url: this.form.url
            };

            this.$http.post('/stream', data).then(response => {
                this.refresh_streams();
            }).catch(err => {
                console.error(err);
                this.form.error = err.statusText;
            });
        }
    },
    created: function () {
        this.refresh_streams();
    }
});
