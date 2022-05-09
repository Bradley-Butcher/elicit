<script>
import Export from "./Export.vue";

export default {
  components: {
    Export,
  },
};
</script>



<template>
  <v-card class="overflow-hidden">
    <v-app-bar absolute color="white" elevate-on-scroll scroll-target="#page">
      <v-app-bar-nav-icon
        @click="$emit('open_sidebar')"
        :class="{ invisible: $route.name != `Document` }"
      ></v-app-bar-nav-icon>

      <v-btn text style="margin-left: 1%">
        <router-link
          style="text-decoration: none; color: inherit"
          :to="{ path: '/' }"
          >Home</router-link
        >
      </v-btn>
      <v-btn text>
        <router-link
          style="text-decoration: none; color: inherit"
          :to="{ path: '/' }"
          >Documents</router-link
        >
      </v-btn>
      <v-btn text>
        <router-link
          style="text-decoration: none; color: inherit"
          :to="{ path: '/performance' }"
          >Performance</router-link
        >
      </v-btn>
      <v-btn text>
        <router-link
          style="text-decoration: none; color: inherit"
          :to="{ path: '/' }"
          >Schemas</router-link
        >
      </v-btn>

      <v-spacer></v-spacer>

      <v-toolbar-title style="position: absolute; left: 50%"
        >Elicit V0.1-pre-alpha</v-toolbar-title
      >

      <v-spacer></v-spacer>

      <Export></Export>

      <v-btn icon>
        <v-icon>mdi-school</v-icon>
      </v-btn>

      <v-btn icon>
        <v-icon>mdi-filter</v-icon>
      </v-btn>
    </v-app-bar>
    <v-sheet id="page" class="overflow-y-auto" style="height: 100vh">
      <slot style="height: 100%"></slot>
    </v-sheet>
  </v-card>
</template>

<style scoped>
.invisible {
  visibility: hidden;
}
</style>