<template>
  <v-expansion-panels accordion id="variable_panel">
    <CategoryItem
      v-for="(value, name, index) in values_data"
      :key="index"
      :value_data="value"
      :value_name="name"
    ></CategoryItem>
  </v-expansion-panels>
</template>

<script>
import axios from "axios";
import CategoryItem from "./CategoryItem.vue";
export default {
  name: "CategoryList",
  components: { CategoryItem },
  data() {
    return {
      values_data: [],
    };
  },
  props: {
    document_name: {
      type: String,
      required: true,
    },
    variable_name: {
      type: String,
      required: true,
    },
  },
  methods: {
    document_extractions() {
      const path =
        "http://127.0.0.1:5000/api/document_extractions/" +
        this.document_name +
        "/" +
        this.variable_name;
      axios
        .get(path)
        .then((res) => {
          this.values_data = res.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  watch: {
    document_name: function () {
      this.document_extractions();
    },
    variable_name: function () {
      this.document_extractions();
    },
  },
};
</script>

<style scoped>
</style>
