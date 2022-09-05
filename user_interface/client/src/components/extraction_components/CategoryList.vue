<template>
  <v-expansion-panels accordion id="variable_panel">
    <CategoryItem
      v-for="(value, name, index) in this.sorted_values(values_data)"
      :key="index"
      :value_data="value"
      :value_name="name"
      @update_extraction="update_extraction"
      @remove_option="remove_option"
      :training_state="training_state"
    ></CategoryItem>
  </v-expansion-panels>
</template>

<script>
import axios from "axios";
import CategoryItem from "./CategoryItem.vue";
import $ from "jquery";
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
    training_state: {
      type: Boolean,
      required: true,
    },
  },
  methods: {
    sorted_values(values) {
      let items = Object.keys(values).map(function (key) {
        return [key, values[key]];
      });
      items.sort(function (first, second) {
        if (first[1].confidence && second[1].confidence) {
          return second[1].confidence - first[1].confidence;
        } else if (first[1].agreement && second[1].agreement) {
          return (
            parseInt(second[1].agreement[0]) - parseInt(first[1].agreement[0])
          );
        } else {
          return 0;
        }
      });
      let sorted_obj = {};
      $.each(items, function (k, v) {
        let use_key = v[0];
        let use_value = v[1];
        sorted_obj[use_key] = use_value;
      });
      return sorted_obj;
    },
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
    update_extraction(value_name, extraction_id, extraction) {
      // copy
      var extractions = this.values_data[value_name].extractions;
      // get idx of extractions where extraction_id == extraction_id if can't find, add new one
      var e_idx = extractions.findIndex(
        (extraction) => extraction.extraction_id == extraction_id
      );
      if (e_idx == -1) {
        extractions.push(extraction);
      } else {
        extractions.splice(e_idx, 1, extraction);
      }
    },
    remove_option(value_name, extraction_id) {
      // copy
      var extractions = this.values_data[value_name].extractions;
      // get idx of extractions where extraction_id == extraction_id
      var e_idx = extractions.findIndex(
        (extraction) => extraction.extraction_id == extraction_id
      );
      extractions.splice(e_idx, 1);
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
