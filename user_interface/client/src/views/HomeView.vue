<template>
  <div>
    <h1 class="mx-auto mt-3" style="text-align: center">Documents</h1>
    <StatusTable id="status_table" :document_list="document_display_list"></StatusTable>
    <div class="ms-5 mt-5" style="height:20%">
      <v-btn depressed dark class="me-3">Upload Documents</v-btn>
      <v-btn depressed dark class="me-3">Sort Documents (Train)</v-btn>
      <TrainButton></TrainButton>
    </div>
  </div>
</template>

<script>
import StatusTable from "../components/StatusTable.vue";
import TrainButton from "../components/TrainButton.vue";

export default {
  name: "App",
  components: {
    StatusTable,
    TrainButton
  },
  props: {
    sidebar: {
      type: Boolean,
      default: false,
    },
    document_display_list: {
      type: Array,
    },
  },
 
};
</script>

<style scoped>
#status_table {
  max-width: 90%;
  margin: auto;
  margin-top: 2%;
}
</style>