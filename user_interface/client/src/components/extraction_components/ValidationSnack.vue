<template>
  <v-snackbar v-model="snackbar" :timeout="5000" class="pr-4">
    Validated extraction!
    <v-btn color="green" text @click="revert_extraction">Oh no, Undo!</v-btn>
  </v-snackbar>
</template>

<script>
export default {
  name: "ValidationSnack",
  props: {
    extraction: {
      type: Object,
    },
    showing: {
      type: Boolean,
    },
  },
  data() {
    return {
      snackbar: false,
    };
  },
  watch: {
    showing: function () {
      this.snackbar = this.showing;
    },
    snackbar: function () {
      if (this.snackbar == false) {
        this.$emit("snackClosed");
      }
    },
  },
  methods: {
    revert_extraction() {
      this.$emit("revert");
      this.snackbar = false;
    },
  },
};
</script>

<style scoped>
.bold {
  font-weight: bold;
}
</style>