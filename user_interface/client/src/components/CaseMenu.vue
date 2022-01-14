<template>
  <div
    class="d-flex flex-column flex-shrink-0 p-3 text-white bg-dark" data-spy="affix" data-offset-top="0"
    style="width: 20%; height: 150vh; overflow-y: auto"
  >
      <span class="fs-4" style="text-align">Main Pages</span>
    <hr style="margin-bottom:0;"/>
    <ul class="nav nav-pills flex-column mb-auto" data-spy="affix" data-offset-top="0">
      <li class="nav-item">
        <a href="#" class="nav-link text-white" aria-current="page"> About </a>
      </li>
      <li>
        <a href="#" class="nav-link text-white"> Guide </a>
      </li>
      <li>
        <a href="#" class="nav-link text-white"> Stats </a>
      </li>
    <span class="fs-4" style="margin-top:16;">Documents</span>
    <hr style="margin-bottom:0;"/>
      <li v-for="c in menu" :key="c.title">
          <a :class="{active: c.case_id == selected_case}" class="nav-link text-white" @click="onItemClick(c)"> {{ c.title }} </a>
          <div class="text-dark" style="height:2px;" :style="styles[case_id]"></div>
      </li>
    </ul>
    <hr />
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      page: 1,
      base_menu: [
        { header: "Main" },
        { title: "Stats" },
        { title: "Guide" },
        { title: "About" },
      ],
      menu: [],
      selected_case: "",
      styles: {},
    };
  },
  methods: {
    getStyle(case_id) {
      const path = "http://127.0.0.1:5000/api/get_response_statuses/" + case_id;
      axios
        .get(path)
        .then((res) => {
            let complete = (res.data.complete / res.data.total) * 100;
            let partial = (res.data.partial / res.data.total) * 100;
            let style = {
                "background": `linear-gradient(to right, #00bcd4 ${complete}%, #b3e5fc ${partial}%)`,
            };
            this.styles[case_id] = style;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    getMessage() {
      const path = "http://127.0.0.1:5000/api/get_cases/" + this.page;
      axios
        .get(path)
        .then((res) => {
          this.menu = res.data;
          const first_case = res.data[0].case_id;
          this.$emit("clicked", first_case);
          this.selected_case = first_case;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    onItemClick(item) {
      this.selected_case = item.case_id;
      this.$emit("clicked", item.case_id);
    },
  },
  created() {
    this.getMessage();
    for (let i = 0; i < this.menu.length; i++) {
      this.getStyle(this.menu[i].case_id);
    }
  },
};
</script>

<style scoped>
.nav-pills .nav-link.active, .nav-pills .show > .nav-link {
    background-color: #2f3338;
}
</style>