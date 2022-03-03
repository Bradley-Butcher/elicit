<template>
  <v-btn depressed dark type="button" class="btn btn-outline-dark btn-sm" @click="clicked">
    <span>{{ button_text }}</span>
    <span
      class="spinner-border spinner-border-sm"
      role="status"
      aria-hidden="true"
      v-if="loading"

    ></span>
  </v-btn>
</template>

<script>
import axios from "axios";

export default({
    data(){
        return {
            loading: false,
        }
    },
    methods: {
        clicked() {
            this.loading = true;
            const path = "http://127.0.0.1:5000/api/update_confidence/";
            axios
                .get(path)
                .then(() => {
                    this.loading = false;
                    this.$emit("retrained");
                })
                .catch((error) => {
                // eslint-disable-next-line
                console.error(error);
                });
        },
        
    },
    computed: {
        button_text() {
            return this.loading ? '' : 'Sort Values (Train)';
        }
    },
})
</script>
