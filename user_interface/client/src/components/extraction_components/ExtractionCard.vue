<template>
  <div>
    <v-hover v-slot="{ hover }">
      <!-- background f3e5f550 if hover else f3e5f580 -->
      <v-card
        class="extraction_card"
        outlined
        width="300"
        height="150"
        :elevation="hover ? 3 : 1"
        @click.stop="showModalNow = !showModalNow"
      >
        <v-card-text>
          <div class="text-overline mb-1">{{ lf }} | {{ confidence }}</div>
          <div class="mx-4 text-center font-weight-light">
            <span class="text-lg-h6">“</span>
            {{ shorten_text(extraction.local_context, 50) }}
            <span class="text-lg-h6">”</span>
          </div>
          <div style="position: absolute; left: 125px; top: 110px">
            <i
              class="fas fa-check fa-xl check mr-2"
              :class="{ valid: extraction.valid == 'TRUE' }"
              @click.stop="set_extraction_answer('TRUE')"
            ></i>
            <i
              class="fas fa-times fa-xl check ml-2"
              :class="{ valid: extraction.valid == 'FALSE' }"
              @click.stop="set_extraction_answer('FALSE')"
            ></i>
          </div>
        </v-card-text> </v-card
    ></v-hover>
    <ContextModal
      :evidence="extraction"
      :showModal="showModalNow"
      @closeModal="showModalNow = false"
    ></ContextModal>
    <ValidationSnack
      :showing="snackShowing"
      :extraction="extraction"
      @snackClosed="snackShowing = false"
      @revert="revert_validation"
    ></ValidationSnack>
    <TrainingDialog
      :open="explaination_modal"
      :context="explain_context"
      :initial_selection="extraction.exact_context"
      @confirm="confirm_training_data"
      @furtherContext="explain_context = extraction.wider_context"
    ></TrainingDialog>
  </div>
</template>

<script>
import axios from "axios";
import ContextModal from "./../ContextModal.vue";
import ValidationSnack from "./ValidationSnack.vue";
import TrainingDialog from "./../TrainingDialog.vue";

export default {
  name: "ExtractionCard",
  components: {
    ContextModal,
    ValidationSnack,
    TrainingDialog,
  },
  props: {
    extraction: {
      type: Object,
      required: true,
      default: () => ({}),
    },
    training_state: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      showModalNow: false,
      snackShowing: false,
      lastExtraction: null,
      explain_context: "",
      explaination_modal: false,
    };
  },
  methods: {
    shorten_text(text, max_length) {
      if (text == null) {
        return "";
      }
      if (text.length > max_length) {
        return text.substring(0, max_length) + "...";
      }
      return text;
    },
    update_extraction(extraction_id, extraction) {
      this.$emit("update_extraction", extraction_id, extraction);
    },
    set_extraction_answer(answer) {
      if (answer == this.extraction.valid) {
        answer = null;
      }
      const path =
        "http://127.0.0.1:5000/api/submit_answer/" +
        this.extraction.extraction_id +
        "/" +
        answer;
      axios
        .post(path)
        .then(() => {
          var copy = Object.assign({}, this.extraction);
          copy.valid = answer;
          if (!this.snackShowing) {
            this.snackShowing = true;
            this.lastExtraction = answer;
          } else {
            this.lastExtraction = null;
          }
          this.update_extraction(copy.extraction_id, copy);
          if (
            this.training_state &&
            answer == "TRUE" &&
            this.extraction.exact_context != null
          ) {
            this.explaination_modal = true;
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    revert_validation() {
      this.set_extraction_answer(this.lastExtraction);
    },
    confirm_training_data(highlight) {
      const path =
        "http://127.0.0.1:5000/api/submit_explaination/" +
        this.extraction.extraction_id +
        "/" +
        highlight;
      axios
        .get(path)
        .then(() => {
          this.explaination_modal = false;
          // update extracted_data where extraction_id = this.clicked_extraction.extraction_id
          for (const i in this.extracted_data) {
            if (
              this.extracted_data[i].extraction_id ==
              this.clicked_extraction.extraction_id
            ) {
              this.extracted_data[i].validated_context = highlight;
            }
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  mounted() {
    this.explain_context = this.extraction.local_context;
  },
  watch: {
    explaination_modal: function () {
      this.explain_context = this.extraction.local_context;
    },
  },
  computed: {
    lf() {
      if (this.extraction.lfs.length == 1) {
        return this.extraction.lfs[0].lf;
      } else {
        return "multiple (" + this.extraction.lfs.length + ")";
      }
    },
    confidence() {
      if (this.extraction.meta_confidence != null) {
        return this.extraction.meta_confidence * 100;
      } else {
        // join list of confidences with a comma
        return this.extraction.lfs
          .map((lf) => Math.round(lf.lf_confidence * 100))
          .join(", ");
      }
    },
  },
};
</script>

<style scoped>
@import "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css";

.check:hover {
  color: rgb(104, 211, 5);
  cursor: pointer;
}

.extraction_card:hover {
  background-color: "#f3e5f580";
}

.valid {
  color: rgb(104, 211, 5);
}
</style>