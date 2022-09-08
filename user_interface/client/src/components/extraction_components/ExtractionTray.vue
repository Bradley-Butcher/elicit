<template>
  <div id="extraction_tray" class="m-4">
    <v-row v-dragscroll.x class="fill-height fill-width" justify="start">
      <v-col
        class="fill-height"
        v-for="(extraction, index) in sorted_extractions"
        :key="index"
      >
        <ExtractionCard
          :extraction="extraction"
          @update_extraction="update_extraction"
          @remove_option="remove_option"
          @revert="revert"
          :training_state="training_state"
        ></ExtractionCard>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import ExtractionCard from "./ExtractionCard.vue";
import { dragscroll } from "vue-dragscroll";
export default {
  directives: {
    dragscroll,
  },
  props: {
    extractions: {
      type: Array,
      required: true,
    },
    training_state: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      last_removed: {},
    };
  },
  //   mounted() {
  //     this.card_width = this.$el.parentElement.clientWidth / this.n_tiles;
  //     this.tray_width =
  //       (this.$el.parentElement.clientWidth / this.n_tiles) *
  //       this.extractions.length;
  //   },
  components: { ExtractionCard },
  methods: {
    sort_extractions(extraction, reverse) {
      return extraction.sort((a, b) => {
        // sum lfs lf_confidence
        let a_sum = a.lfs.reduce((acc, lf) => {
          return acc + lf.lf_confidence;
        }, 0);
        let b_sum = b.lfs.reduce((acc, lf) => {
          return acc + lf.lf_confidence;
        }, 0);
        if (reverse) {
          return b_sum - a_sum;
        } else {
          return a_sum - b_sum;
        }
      });
    },
    update_extraction(extraction_id, answer) {
      this.$emit("update_extraction", extraction_id, answer);
    },
    remove_option(extraction_id) {
      this.last_removed = this.extractions.find(
        (extraction) => extraction.id == extraction_id
      );
      this.$emit("remove_option", extraction_id);
    },
    revert() {
      this.$emit(
        "update_extraction",
        this.last_removed.extraction_id,
        this.last_removed
      );
    },
  },
  computed: {
    sorted_extractions() {
      return this.sort_extractions(this.extractions, true);
    },
  },
};
</script>

<style scoped>
#extraction_tray {
  overflow-x: hidden;
  overflow-y: hidden;
}
.fill-width {
  overflow-x: hidden;
  overflow-y: hidden;
  flex-wrap: nowrap;
}
</style>