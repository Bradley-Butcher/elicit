<script>
import CaseNav from "../components/CaseNav.vue";
import CaseMenu from "../components/CaseMenu.vue";

export default {
  name: "DocumentView",
  components: {
    CaseNav,
    CaseMenu,
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
        this.$router.push({
          name: "Document",
          params: { id: this.document_display_list[idx - 1].case_id },
        });
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
    <v-content style="height: 100%">
      <v-container
        fluid
        style="
          margin: 0px;
          padding: 0px;
          max-width: 100%;
          height: 100%;
          overflow: hidden;
        "
      >
        <v-row class="fill-height">
          <v-col
            class="ma-0 pa-0 fill-height fill-width"
            cols="9"
            align="center"
          >
            <CaseNav
              id="case_area"
              :current_case="$route.params.id"
              :refresh_case="refresh_case"
              style="max-width: 100%"
            />
          </v-col>
          <v-col
            class="ma-0 pa-0"
            align="center"
            style="max-height: 100%"
            cols="3"
          >
            <v-row id="summary" class="ma-0 pa-0 temp" style="height: 40%">
              <v-col align="center">Summary</v-col> </v-row
            ><v-divider class="ma-0 pa-0"></v-divider>
            <v-row id="stats" class="ma-0 pa-0 temp" style="height: 30%">
              <v-col align="center">Stats</v-col> </v-row
            ><v-divider class="ma-0 pa-0"></v-divider>
            <v-row id="controlpanel" class="ma-0 pa-0 temp" style="height: 30%">
              <v-col align="center">
                <h5 class="ma-2 pa-2">Document: {{ active_case }}</h5>
                <v-row>
                  <v-col align="center">
                    <v-btn tile depressed @click="getPrevDocument" width="40px">
                      <v-icon right dark raised class="me-2">
                        mdi-arrow-left-bold
                      </v-icon>
                    </v-btn>
                    <v-btn tile depressed @click="getNextDocument" width="40px">
                      <v-icon right dark raised> mdi-arrow-right-bold </v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
    </v-content>
    <CaseMenu
      @clicked="onCaseClicked"
      :active_case="active_case"
      style="float: left"
      :sidebar="sidebar"
      :document_list="document_display_list"
    />
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

#controlpanel {
  background-color: rgb(210, 213, 213, 0.5);
}

#summary {
  background-color: #88fad650;
}

#stats {
  background-color: #fad6fa50;
}
</style>