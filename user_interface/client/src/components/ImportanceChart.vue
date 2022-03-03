<template>
  <div style="height: 100%; padding: 1% 15% 10% 15%">
    <h2 style="text-align: center">Labelling Function Importance</h2>

    <v-progress-circular
      :size="70"
      :width="7"
      color="purple"
      indeterminate
      style="z-index: 1; position: absolute; top: 40%; left: 50%"
      :style="{ visibility: loaded ? 'hidden' : 'visible' }"
    ></v-progress-circular>
    <canvas id="ImportanceChart" style="z-index: 2"></canvas>
  </div>
</template>

<script>
import axios from "axios";
import Chart from "chart.js/auto";

export default {
  name: "FunctionImportance",
  data() {
    return {
      dataset_data: [],
      loaded: false,
      switch_on: false,
      items: [],
      active_chart: null,
      selected: "",
    };
  },
  methods: {
    get_data: async function () {
      const path =
        "http://127.0.0.1:5000/api/get_accuracy";
      await axios
        .get(path)
        .then((res) => {
          this.dataset_data = res.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    get_variables: async function () {
      const path =
        "http://127.0.0.1:5000/api/get_variable_list"
      await axios
        .get(path)
        .then((res) => {
          this.items = res.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    buildChart(data) {
      var ctx = document.getElementById("ImportanceChart").getContext("2d");
      if (this.active_chart) {
        this.active_chart.destroy();
      }
      this.active_chart = new Chart(ctx, {
        type: "bar",
        data: data,
        options: {
          plugins: { legend: { display: false } },
          maintainAspectRatio: false,
          responsive: true,
          indexAxis: "y",
          scales: {
            x: {
              min: 0, // minimum value
              max: 1, // maximum value
            },
          },
        },
      });
    },
  },
  watch: {
    switch_on: async function (new_value) {
      this.loaded = false;
      await this.get_data("offenses", new_value);
      this.loaded = true;
      this.buildChart(this.dataset_data);
    },
    selected: async function (new_value) {
      this.loaded = false;
      await this.get_data(new_value, this.switch_on);
      this.loaded = true;
      this.buildChart(this.dataset_data);
    },
  },
  mounted: async function () {
    await this.get_variables();
    this.selected = this.items[0];
    await this.get_data(this.selected, this.switch_on);
    this.loaded = true;
    this.buildChart(this.dataset_data);
  }
};
</script>