<template>
  <div>
    <v-dialog persistent v-model="open" max-width="30%">
      <v-card>
        <v-card-title class="text-h5"> Explaination Highlighter </v-card-title>
        <v-divider class="p-0"></v-divider>
        <Highlight ref="highlightReference" @highlighted="addHighlighted">
          <v-card-text v-html="display_context"></v-card-text>
        </Highlight>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="green darken-1"
            text
            @click="furtherContext"
            :disabled="max_context"
          >
            Further Context
          </v-btn>
          <v-btn color="green darken-1" text @click="signalConfirm">
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import Highlight from "./Highlight.vue";
export default {
  name: "TrainingDialog",
  methods: {
    signalConfirm() {
      this.$emit("confirm", this.highlight);
      this.max_context = false;
    },
    furtherContext() {
      this.$emit("furtherContext");
      this.max_context = true;
    },

    addHighlighted(data) {
      this.highlight = data.selected;
      this.applyHighlights();
    },
    applyHighlights() {
      let text = this.context.replace(
        new RegExp(this.highlight, "gi"),
        (match) => {
          return (
            '<span style="background-color: ' +
            this.color +
            '">' +
            match +
            "</span>"
          );
        }
      );
      this.display_context = text;
    },
  },
  props: {
    context: {
      type: String,
      required: true,
    },
    open: {
      type: Boolean,
      default: false,
    },
    initial_selection: {
      type: String,
      default: "",
    },
    color: {
      type: String,
      default: "#FFEE58",
    },
  },
  data: () => ({
    highlight: null,
    display_context: null,
    max_context: false,
  }),
  watch: {
    context: {
      handler() {
        this.display_context = this.context;
      },
      deep: true,
    },
    initial_selection: {
      handler() {
        this.addHighlighted({ selected: this.initial_selection });
      },
      deep: true,
    },
  },
  mounted() {
    this.max_context = false;
  },
  components: { Highlight },
};
</script>

<style scoped>
</style>