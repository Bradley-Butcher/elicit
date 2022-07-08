<template>
  <div>
    <h5 class="ma-2 pa-2">Document: {{ active_case }}</h5>
    <v-row justify="center">
      <v-col align="center" class="p-0 ma"><h6>Document:</h6></v-col>
      <v-col align="center" class="p-0 m-0">
        <v-btn tile depressed class="m-0 p-0" @click="signalPrev" width="40px">
          <v-icon right dark raised class="me-2"> mdi-arrow-left-bold </v-icon>
        </v-btn>
        <v-btn tile depressed class="m-0 p-0" @click="signalNext" width="40px">
          <v-icon right dark raised> mdi-arrow-right-bold </v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-row style="max-height: 50px">
      <v-col style="max-height: 50px">
        <h6>Training Mode:</h6>
      </v-col>
      <v-col style="max-height: 50px">
        <v-switch
          class="m-0 p-0"
          v-model="training_switch"
          @change="signalTraining"
          :label="`Training: ${training_switch.toString()}`"
        ></v-switch>
      </v-col>
    </v-row>
  </div>
</template>

<script>
export default {
  name: "ControlPanel",
  methods: {
    signalPrev() {
      this.$emit("signalPrev");
    },
    signalNext() {
      this.$emit("signalNext");
    },
    signalTraining() {
      this.$emit("signalTraining", this.training_switch);
    },
  },
  data() {
    return {
      training_switch: false,
    };
  },
  props: {
    active_case: {
      type: String,
      required: true,
    },
  },
};
</script>

<style scoped>
</style>