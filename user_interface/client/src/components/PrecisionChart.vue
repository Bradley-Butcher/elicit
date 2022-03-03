<template>
  <div style="height: 100%; padding: 1% 15% 10% 15%">
    <h2 style="text-align: center">Precision</h2>
    <v-row justify="start" align="start">
      <v-col>
        <v-select
          :items="items"
          v-model="selected"
          label="Variable"
          outlined
          style="width: 15%;"
        ></v-select>
      </v-col>
      <v-col>
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }"
            ><div v-on="on" v-bind="attrs" style="width:250px;height:30px">
              <v-switch
                v-model="switch_on"
                v-bind="attrs"
                v-on="on"
                :label="`Boolean Confidence: ${switch_on.toString()}`"
                width="200px"
              ></v-switch>
            </div> </template
          ><span>Whether to calculate precision using: (1) continuous confidence levels or (2) boolean > 0. <br> Refer to help for more information.</span></v-tooltip
        >
      </v-col>
    </v-row>

    <v-progress-circular
      :size="70"
      :width="7"
      color="purple"
      indeterminate
      style="z-index: 1; position: absolute; top: 40%; left: 50%"
      :style="{ visibility: loaded ? 'hidden' : 'visible' }"
    ></v-progress-circular>
    <canvas id="myChart" style="z-index: 2"></canvas>
  </div>
</template>

<script>
import axios from "axios";
import Chart from "chart.js/auto";

export default {
  name: "PrecisionChart",
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
    get_data: async function (variable_name, binary) {
      const path =
        "http://127.0.0.1:5000/api/get_precision/" +
        variable_name +
        "/" +
        binary;
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
      var ctx = document.getElementById("myChart").getContext("2d");
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