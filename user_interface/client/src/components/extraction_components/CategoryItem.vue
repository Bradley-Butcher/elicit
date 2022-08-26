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
                Confidence: {{ value_data.confidence }}
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
              <div class="font-weight-bold">Evidence: unknown</div></v-card
            ></v-col
          >
          <v-col md="2" offset-md="3" align="right">
            <v-card
              align="center"
              class="pa-1 ml-auto"
              :class="{
                answered: value_data.valid && value_data.valid != 'null',
                unanswered: !value_data.valid || value_data.valid == 'null',
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
      <ExtractionTray :extractions="extractions"></ExtractionTray>
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
  },
  computed: {
    extractions() {
      return this.value_data.extractions;
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