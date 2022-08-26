<template>
  <v-hover v-slot="{ hover }">
    <!-- background f3e5f550 if hover else f3e5f580 -->
    <v-card
      class="extraction_card"
      outlined
      width="300"
      height="150"
      :elevation="hover ? 3 : 1"
    >
      <v-card-text>
        <div class="text-overline mb-1">
          {{ shorten_text(extraction.lf, 15) }} |
          {{ extraction.lf_confidence * 100 }}%
        </div>
        <div class="mx-4 text-center font-weight-light">
          <span class="text-lg-h6">“</span>
          {{ extraction.local_context }}
          <span class="text-lg-h6">”</span>
        </div>
        <div style="position: relative; left: 0px; top: 25px">
          <i
            class="fas fa-check fa-xl check mr-2"
            :class="{ valid: extraction.valid == 'TRUE' }"
          ></i>
          <i
            class="fas fa-times fa-xl check ml-2"
            :class="{ valid: extraction.valid == 'FALSE' }"
          ></i>
        </div>
      </v-card-text> </v-card
  ></v-hover>
</template>

<script>
export default {
  name: "ExtractionCard",
  props: {
    extraction: {
      type: Object,
      required: true,
    },
  },
  methods: {
    shorten_text(text, max_length) {
      if (text.length > max_length) {
        return text.substring(0, max_length) + "...";
      }
      return text;
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