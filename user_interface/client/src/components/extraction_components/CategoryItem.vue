<template>
  <v-expansion-panel>
    <v-expansion-panel-header class="p-0">
      <v-container class="pl-3 pr-0 pt-2 pb-2 m-0" width="1500px">
        <v-row no-gutters justify="start">
          <v-col md="2" align="left">
            <v-card
              class="pa-2"
              elevation="0"
              outlined
              style="background-color: #f9fbe7"
              max-width="150px"
              align="center"
            >
              <div class="font-weight-bold">Value: {{ value_name }}</div>
            </v-card>
          </v-col>
          <v-col md="2" align="left" class="pl-4">
            <v-card
              class="pa-2"
              elevation="0"
              outlined
              style="background-color: #f3e5f5"
              max-width="150px"
              align="center"
            >
              <div class="font-weight-bold">
                {{
                  value_data.confidence
                    ? "Confidence: " +
                      Math.round(value_data.confidence * 100) +
                      "%"
                    : "Agreement: " + value_data.agreement
                }}
              </div></v-card
            ></v-col
          >
          <v-col md="3" align="left" class="pl-4">
            <v-card
              class="pa-2"
              elevation="0"
              outlined
              style="background-color: #eceff1"
              max-width="150px"
            >
              <div class="font-weight-bold">
                Evidence: {{ exact_context }}
              </div></v-card
            ></v-col
          >
          <v-col md="2" offset-md="3" align="right">
            <v-card
              align="center"
              class="pa-1 ml-auto"
              :class="{
                answered: status,
                unanswered: !status,
              }"
              :elevation="status ? 1 : 0"
              outlined
              tile
              disabled
              max-width="100px"
            >
              <div>validated</div>
            </v-card></v-col
          >
        </v-row></v-container
      >
    </v-expansion-panel-header>
    <v-expansion-panel-content padding="0">
      <ExtractionTray
        :extractions="extractions"
        @update_extraction="update_extraction"
        @remove_option="remove_option"
        :training_state="training_state"
      ></ExtractionTray>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script>
import ExtractionTray from "./ExtractionTray.vue";

export default {
  name: "CategoryItem",
  props: {
    value_data: {
      type: Object,
      required: true,
    },
    value_name: {
      type: String,
      required: true,
    },
    training_state: {
      type: Boolean,
      required: true,
    },
  },
  methods: {
    update_extraction(extraction_id, extraction) {
      this.$emit(
        "update_extraction",
        this.value_name,
        extraction_id,
        extraction
      );
    },
    remove_option(extraction_id) {
      this.$emit("remove_option", this.value_name, extraction_id);
    },
  },
  computed: {
    //iterate over this.value_data.extractions, return true is valid is ever "TRUE"
    status() {
      return this.value_data.extractions.some((extraction) => {
        return extraction.valid == "TRUE";
      });
    },
    extractions() {
      return this.value_data.extractions;
    },
    exact_context() {
      //return exact context with maximum confidence from value_data.extractions list
      let max_confidence = 0;
      let exact_context = "";
      this.value_data.extractions.forEach((extraction) => {
        if (extraction.confidence > max_confidence) {
          max_confidence = extraction.meta_confidence;
          exact_context = extraction.exact_context;
        }
      });
      if (max_confidence > 0) return exact_context;
      if (max_confidence == 0) {
        this.value_data.extractions.forEach((extraction) => {
          extraction.lfs.forEach((lf) => {
            if (lf.lf_confidence > max_confidence) {
              max_confidence = lf.lf_confidence;
              exact_context = extraction.exact_context;
            }
          });
        });
      }
      return exact_context;
    },
  },
  components: { ExtractionTray },
};
</script>

<style scoped>
.v-expansion-panel-content >>> .v-expansion-panel-content__wrap {
  padding: 0 !important;
}

.unanswered {
  background-color: #ffffff;
  color: #000000;
  text-decoration: line-through;
}

.answered {
  background-color: #4caf50;
  color: #150000;
  text-decoration: none;
}
</style>