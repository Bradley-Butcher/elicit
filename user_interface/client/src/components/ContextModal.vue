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
    <v-dialog
        transition="dialog-top-transition"
        max-width="60%"
        v-model="dialog"
        data-app
      >
    <template v-slot:default="dialog">
    <v-card>
      <v-toolbar color="2a2a2e" dark>Wider context for labelling function: {{ modal_title }}</v-toolbar>
      <v-card-text>
        <div class="text pa-12">{{formatted_context}}</div>
      </v-card-text>
      <v-card-actions class="justify-end">
        <v-btn text @click="dialog.value = false">Close</v-btn>
      </v-card-actions>
    </v-card>
    </template>
    </v-dialog>
</template>

<script>
export default {
  name: "EvidenceModal",
  emits: ["closeModal"],
  props: {
    showModal: Boolean,
    evidence: {
      type: Object,
    },
  },
  watch: {
    showModal() {
        this.dialog = !this.dialog;
    }
  },
  data() {
    return {
      active: this.showModal,
      dialog: false,
    };
  },
  computed: {
    formatted_context() {
      if (
        this.evidence["wider_context"] == "N/A" ||
        this.evidence["wider_context"] == null
      ) {
        return "The extractor in question did not capture any relevant information from the document.";
      } else {
        return this.evidence["wider_context"];
      }
    },
    modal_title() {
      return this.evidence["method"];
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