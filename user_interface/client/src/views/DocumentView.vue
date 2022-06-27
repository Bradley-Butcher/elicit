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
      this.$router.push({ name: "Document", params: { id: value } });
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
  <div>
    <v-content>
      <v-container fluid fill-height style="margin: 0px; padding: 0px; max-width: 99%">
        <v-row :align="center" style="height: 250px;">
          <v-col class="cblock" align="center" cols=5>
            <h3 class="ma-2 pa-2">Control Panel</h3>
            <v-btn tile depressed @click="getPrevDocument">
              <v-icon right dark raised class="me-2">
                mdi-arrow-left-bold
              </v-icon>
              Previous Document
            </v-btn>

            <v-btn tile depressed @click="getNextDocument">
              Next Document
              <v-icon right dark raised>
                mdi-arrow-right-bold
              </v-icon>
            </v-btn>

          </v-col>
          <!-- transparent temp backgrund to show area under development -->
          <v-col class="cblock" style="background-color:aqua;">
          <v-row align="center" justify="center">
          <v-col class="d-flex justify-center align-center"><h3>Reserved Space for Document Summary</h3></v-col>
          </v-row>
            
          </v-col>
        </v-row>
        <v-row class="fill-height">
          <v-col class="cblock ma-0 pa-0 fill-height" align="center">
            <CaseNav id="case_area" :current_case="$route.params.id" :refresh_case="refresh_case"
              style="max-width:95%" />
          </v-col>
        </v-row>
      </v-container>
    </v-content>
    <CaseMenu @clicked="onCaseClicked" :active_case="active_case" style="float: left" :sidebar="sidebar"
      :document_list="document_display_list" />
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