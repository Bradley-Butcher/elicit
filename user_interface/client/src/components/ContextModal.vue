<template>
  <!-- <div
      ref="modal"
      class="modal fade"
      :class="{ show: active, 'd-block': active }"
      tabindex="-1"
      role="dialog"
    >
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header text-center">
            <h5 class="modal-title w-100">
              Wider context for labelling function: {{ modal_title }}
            </h5>
            <button
              type="button"
              class="btn-close"
              data-dismiss="modal"
              aria-label="Close"
              v-on:click="$emit('closeModal')"
            ></button>
          </div>
          <div class="modal-body text-dark">
            <blockquote class="blockquote">
              <p class="mb-0">
                {{ formatted_context }}
              </p>
            </blockquote>
          </div>
          <div class="modal-footer text-dark">
            <button
              type="button"
              class="btn btn-primary mx-auto"
              v-on:click="$emit('closeModal')"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div> -->
  <v-dialog max-width="60%" v-model="dialog" data-app>
    <v-card>
      <!-- <v-card-text>
        <div class="text pa-12">{{ formatted_context }}</div>
      </v-card-text> -->

      <v-card-text>
        <div class="text-overline pa-6" style="text-align: center">
          {{ lf }} | {{ confidence }}
        </div>
        <div class="mx-2 text-center font-weight-light">
          <span class="text-lg-h6"></span>

          <span class="text-lg-h6">“</span>
          <span v-html="formatted_context"></span>
          <span class="text-lg-h6">”</span>
        </div>
      </v-card-text>

      <v-card-actions class="justify-end">
        <v-btn text @click="dialog = false">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: "ContextModal",
  emits: ["closeModal"],
  props: {
    showModal: Boolean,
    evidence: {
      type: Object,
    },
  },
  data() {
    return {
      dialog: false,
    };
  },
  watch: {
    showModal() {
      this.dialog = true;
    },
  },
  methods: {
    add_mark(evidence) {
      // replace text substr with <mark>substr</mark>
      if (evidence.valid == "TRUE" && evidence.validated_context) {
        return "<mark>" + evidence.validated_context + "</mark>";
      }
      if (!evidence.exact_context) {
        return "No Evidence";
      }
      if (evidence.exact_context == "N/A") {
        return evidence.exact_context;
      }
      let substr = evidence.exact_context;
      let regex = new RegExp(substr, "gi");
      let new_text = evidence.local_context.replace(
        regex,
        "<mark>" + substr + "</mark>"
      );
      return new_text;
    },
  },
  computed: {
    formatted_context() {
      if (
        this.evidence["wider_context"] == "N/A" ||
        this.evidence["wider_context"] == null
      ) {
        return "The extractor in question did not capture any relevant information from the document.";
      } else {
        return this.add_mark(this.evidence);
      }
    },
    modal_title() {
      return this.evidence.lf;
    },
    lf() {
      if (this.evidence.lfs.length == 1) {
        return this.evidence.lfs[0].lf;
      } else {
        return "multiple (" + this.evidence.lfs.length + ")";
      }
    },
    confidence() {
      if (this.evidence.meta_confidence != null) {
        return this.evidence.meta_confidence * 100;
      } else {
        // join list of confidences with a comma
        return this.evidence.lfs
          .map((lf) => lf.lf + " :  " + Math.round(lf.lf_confidence * 100))
          .join(", ");
      }
    },
  },
};
</script>

<style scoped>
.modal-title {
  background-color: aliceblue;
  color: #000;
}
.modal-header {
  background-color: aliceblue;
  text-align: center;
}
.modal-dialog {
  overflow-y: initial !important;
  overflow-x: initial !important;
}
.model-content {
  height: 60vh;
  width: 70vw;
}
.modal-content {
  width: 900px;
}
.modal-title {
  left: auto;
  right: auto;
}
.modal-body {
  height: 60vh;
  overflow-y: scroll;
  overflow-x: scroll;
}
</style>