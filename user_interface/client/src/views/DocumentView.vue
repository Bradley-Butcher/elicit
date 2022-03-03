<script>
import CaseNav from "../components/CaseNav.vue";
import CaseMenu from "../components/CaseMenu.vue";

export default {
  name: "DocumentView",
  components: {
    CaseNav,
    CaseMenu
  },
  data() {
    return {
      active_case: this.$route.params.id,
      refresh_case: 0,
    };
  },
  methods: {
    onCaseClicked(value) {
      this.$router.push({name: "Document", params: {id: value}});
      this.active_case = value;
    },
    getNextDocument() {
      let idx = this.document_display_list.findIndex(
        (doc) => doc.case_id === this.active_case
      );
      console.log(this.active_case);
      console.log(idx);
      if (idx < this.document_display_list.length - 1) {
        this.$router.push({
          name: "Document",
          params: {
            id: this.document_display_list[idx + 1].case_id,
          },
        });
        this.active_case = this.document_display_list[idx + 1].case_id;

      }
    },
    getPrevDocument() {
      let idx = this.document_display_list.findIndex(
        (doc) => doc.case_id === this.active_case
      );
      if (idx > 0) {
        this.$router.push({ name: "Document", params: { id: this.document_display_list[idx - 1].case_id } });
        this.active_case = this.document_display_list[idx - 1].case_id;
      }
    },
  },
  props: {
    sidebar: {
      type: Boolean,
      default: false,
    },
    document_display_list: {
      type: Array,
    },
  },
};
</script>

<template>
  <div style="height:80vh">
  <div class="d-flex flex-row flex-grow justify-center align-center" style="margin-top:5%;">
    <v-btn tile depressed @click="getPrevDocument">
      <v-icon
        right
        dark
        raised
        class="me-2"
      >
        mdi-arrow-left-bold
      </v-icon>
      Previous Document
  </v-btn>
  <CaseNav
      id="case_area"
      class="d-flex flex-column flex-grow-1"
      :current_case="$route.params.id"
      :refresh_case="refresh_case"
    />
    <v-btn tile depressed @click="getNextDocument">
      Next Document
      <v-icon
        right
        dark
        raised
      >
        mdi-arrow-right-bold
      </v-icon>
  </v-btn>
  </div>

      <CaseMenu @clicked="onCaseClicked" :active_case="active_case" style="float: left" :sidebar="sidebar" :document_list="document_display_list"/>

  </div>
  
</template>

<style lang="scss" scoped>
#case_area {
  max-width: 70%;
  margin-top: 2%;
  margin-bottom: 5%;
  margin-right: 2%;
  margin-left: 2%;

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
</style>