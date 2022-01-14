<template>
  <sidebar-menu
    class="cut-text"
    :menu="menu"
    @item-click="onItemClick"
    :hideToggle="true"
  />
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      page: 1,
      base_menu: [
        {"header": "Main",},
        {"title": "Stats"},
        {"title": "Guide"},
        {"title": "About"},
      ],
      menu: [],
      selected_case: "",
    };
  },
  methods: {
    getMessage() {
      const path = "http://127.0.0.1:5000/api/get_cases/" + this.page;
      axios
        .get(path)
        .then((res) => {
          this.menu = this.base_menu.concat(res.data);
          const first_case = res.data[1].case_id;
          this.$emit("clicked", first_case);
          this.selected_case = first_case;

        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    onItemClick(event, item) {
      this.$emit("clicked", item.case_id);
    },
  },
  created() {
    this.getMessage();
  },
};
</script>

<style scoped>
.v-sidebar-menu .vsm--item {
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}
.v-sidebar-menu .vsm--header {
      font-size: 1.1em;
}

</style>