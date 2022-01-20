<template>
  <a type="button" @click="getData" class="btn btn-outline-dark btn-sm"
    >Export</a
  >
</template>

<script>
import axios from "axios";

export default {
  methods: {
    getData() {
      const path = "http://127.0.0.1:5000/api/get_data/";
      axios
        .get(path)
        .then((res) => {
          var fileURL = window.URL.createObjectURL(new Blob([res.data]));
          var fileLink = document.createElement("a");

          fileLink.href = fileURL;
          fileLink.setAttribute("download", "export.csv");
          document.body.appendChild(fileLink);

          fileLink.click();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    exportData() {
      this.$emit("export");
    },
  },
};
</script>


<style>
</style>