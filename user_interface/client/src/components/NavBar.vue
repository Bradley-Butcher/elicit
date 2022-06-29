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
      <v-row
        class="ma-0 pa-0"
        style="max-height: 100%; width: 100%; flex-grow: 1"
        justify="left"
      >
        <v-col class="ma-0 pa-0" cols="1" align="left" style="max-width: 70px">
          <v-app-bar-nav-icon
            @click="$emit('open_sidebar')"
            :class="{ invisible: $route.name != `Document` }"
          ></v-app-bar-nav-icon>
        </v-col>
        <v-col
          class="ma-0 pa-2"
          cols="2"
          align="center"
          style="max-width: 150px"
        >
          <v-btn text>
            <router-link
              style="text-decoration: none; color: inherit"
              :to="{ path: '/' }"
              >Documents</router-link
            >
          </v-btn>
        </v-col>
        <v-col
          style="max-width: 150px"
          class="ma-0 pa-2"
          cols="2"
          align="center"
        >
          <v-btn text>
            <router-link
              style="text-decoration: none; color: inherit"
              :to="{ path: '/performance' }"
              >Performance</router-link
            >
          </v-btn>
        </v-col>
        <v-col class="ma-0 pa-1" cols="5" align="center">
          <v-toolbar-title>Elicit V0.1-pre-alpha</v-toolbar-title>
        </v-col>
        <v-col style="max-width: 70px" class="ma-0 pa-0" cols="1" align="right">
          <Export></Export>
        </v-col>
      </v-row>
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