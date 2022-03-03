<script>
import NavBar from "./components/NavBar.vue";
import axios from "axios";

export default {
  
  name: "App",
  components: {
    NavBar
  },
  data() {
    return {
      sidebar_open: false,
      document_display_list: [],
    };
  },
  methods: {
    updateDocList(doc_list) {
      this.document_display_list = doc_list;
    },
    getDocuments() {
      const path = "http://127.0.0.1:5000/api/get_cases";
      axios
        .get(path)
        .then((res) => {
          this.document_display_list = res.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  mounted() {
    this.getDocuments();
  },
};
</script>

<template>
<v-app>
  <div id="app">
    <div id="modals"></div>
    <NavBar @open_sidebar="sidebar_open = !sidebar_open">
    <router-view style="height:100vh;padding-top:64px;padding-bottom:64px" @update_doc_list="updateDocList(list)" :document_display_list="document_display_list" :sidebar="sidebar_open"/>
    </NavBar>
    <v-footer
    dark
    padless
    
  >
    <v-card
      flat
      tile
      class="lighten-1 white--text text-center"
      style="height:64px; position:fixed; bottom:0; width:100%"
    >
      <v-card-text class="white--text">
        {{ new Date().getFullYear() }} — <strong>The Turing Institute</strong>
      </v-card-text>
    </v-card>
  </v-footer>
  </div>
  </v-app>  
</template> 

<style lang="scss" scoped>
#case_area {
  margin-left: 25%;
  margin-right: 5%;
}
#main_nav {
  margin-left: 20%;
}
.modalz {
  width: 300px;
  padding: 30px;
  box-sizing: border-box;
  background-color: #fff;
  font-size: 20px;
  text-align: center;
}
.router-link-active{
  color: rgba(0, 0, 0, 0.9);
}
</style>