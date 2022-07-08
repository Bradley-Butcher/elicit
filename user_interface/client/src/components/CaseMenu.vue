<template>
  <div>
    <v-navigation-drawer v-model="active_menu" absolute temporary>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="text-h6"> Documents </v-list-item-title>
          <v-list-item-subtitle> Quick Select </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
      <v-divider></v-divider>

      <v-list dense nav>
        <v-list-item
          v-for="c in document_list"
          :key="c.id"
          link
          :class="{ active: c.case_id == active_case }"
        >
          <v-list-item-content @click="onItemClick(c)">
            <v-list-item-title>{{ c.title }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
  </div>
</template>

<script>
export default {
  data() {
    return {
      page: 1,
      active_menu: null,
      menu: [],
      styles: {},
    };
  },
  props: {
    sidebar: {
      type: Boolean,
      default: false,
    },
    document_list: {
      type: Array,
    },
    active_case: {
      type: String,
      default: null,
    },
  },
  watch: {
    sidebar() {
      this.active_menu = true;
    },
  },
  methods: {
    onItemClick(item) {
      this.$emit("clicked", item.case_id);
    },
  },
};
</script>

<style scoped>
.active {
  background-color: #b3b3b331;
}
</style>