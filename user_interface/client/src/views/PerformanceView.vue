<template>
  <div style="height: 85%">
    <v-carousel v-model="model" height="100%">
      <template v-slot:prev="{ on, attrs }">
        <v-btn color="success" v-bind="attrs" v-on="on">{{ getPrev() }}</v-btn>
      </template>
      <template v-slot:next="{ on, attrs }">
        <v-btn color="info" v-bind="attrs" v-on="on">{{ getNext() }}</v-btn>
      </template>
      <v-carousel-item>
        <v-sheet height="100%" style="padding-bottom: 50px" tile>
          <PrecisionChart
            @update_chart="setChart(chart_obj)"
            @delete_chart="deleteChart"
          ></PrecisionChart>
        </v-sheet>
      </v-carousel-item>
      <v-carousel-item>
        <v-sheet height="100%" style="padding-bottom: 50px" tile>
          <Top1Chart
            @update_chart="setChart(chart_obj)"
            @delete_chart="deleteChart"
          ></Top1Chart>
        </v-sheet>
      </v-carousel-item>
      <v-carousel-item>
        <v-sheet height="100%" style="padding-bottom: 50px" tile>
          <ImportanceChart
            @update_chart="setChart(chart_obj)"
            @delete_chart="deleteChart"
          ></ImportanceChart>
        </v-sheet>
      </v-carousel-item>
    </v-carousel>
  </div>
</template>

<script>
import ImportanceChart from '../components/ImportanceChart.vue';
import PrecisionChart from "../components/PrecisionChart.vue";
import Top1Chart from "../components/Top1Chart.vue";

export default {
  name: "Performance",
  components: { PrecisionChart, Top1Chart, ImportanceChart },
  data() {
    return {
      active_chart: "",
      model: 0,
      charts: ["Precision", "Accuracy", "Importance"],
    };
  },
  methods: {
    setChart(chart_obj) {
      this.active_chart = chart_obj;
    },
    getNext() {
      return this.charts[
        (this.model + this.charts.length + 1) % this.charts.length
      ];
    },
    getPrev() {
      // make it wrap around
      return this.charts[
        (this.model + this.charts.length - 1) % this.charts.length
      ];
    },
    deleteChart() {
      if (this.active_chart) {
        console.log("Deleting");
        this.active_chart.destroy();
        this.active_chart = null;
      }
    },
  },
};
</script>

<style scoped>
</style>