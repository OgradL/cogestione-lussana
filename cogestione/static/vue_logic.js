const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            query: "",
            results: [],
            selected: [],
            loading: false,
            timeout: null,
            selection_str: ""
        };
    },
    methods: {
        search() {
            clearTimeout(this.timeout);

            this.timeout = setTimeout(async () => {
                if (this.query.length < 2) {
                    this.results = [];
                    return;
                }

                this.loading = true;
                const res = await fetch(`/get_students/${this.query}`, {
                    method:"GET",
                });

                this.results = await res.json();
                this.loading = false;
            }, 0);
        },

        clear() {
            this.results = [];
            this.query = "";
            this.loading = false;
            this.timeout = null;
            this.selection_str = "";
        },

        select(email) {

            if (this.results.length == 0)
                return;

            element = this.results[0];
            this.results.forEach((el) => {
                if (el.email == email)
                    element = el;
            });

            this.clear()
            this.selection_str += ";" + email
            this.selected.push(element);
        },

        deselect(email) {
            this.selected = this.selected.filter(x => x.email != email);
            this.selection_str = this.selection_str.replace(email, "")
            this.selection_str = this.selection_str.replace(";;", ";")
        }
    }
}).mount("#search-bar");

