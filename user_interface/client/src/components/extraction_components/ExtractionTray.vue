<template>
  <div id="extraction_tray">
    <v-container class="pt-2">
      <v-row v-dragscroll.x class="fill-height fill-width" justify="start">
        <v-col
          class="fill-height"
          v-for="(extraction, index) in sort_extractions(extractions, true)"
          :key="index"
        >
          <ExtractionCard :extraction="extraction"></ExtractionCard>
        </v-col>
      </v-row>
    </v-container>
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
        if (a.lf_confidence < b.lf_confidence) {
          return reverse ? 1 : -1;
        }
        if (a.lf_confidence > b.lf_confidence) {
          return reverse ? -1 : 1;
        }
        return 0;
      });
    },
  },
};
</script>

<style scoped>
#extraction_tray {
  overflow-x: hidden;
}
.fill-width {
  overflow-x: hidden;
  overflow-y: hidden;
  flex-wrap: nowrap;
}
</style>