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
    dragged(event) {
      //get item
      //get parent
      var parent = document.getElementById("viewrow");
      // get distance of drag
      let clientx = event.clientX;
      if (clientx == 0) {
        return;
      }
      let x = event.clientX - parent.offsetLeft;
      // resize max-width of casecol proportional to drag
      let width = (x / parent.offsetWidth) * 100;
      // set max-width of casecol
      // get item with id casecol
      let casecol = document.getElementById("casecol");
      casecol.style.maxWidth = width + "%";
      // get item
      let sidecol = document.getElementById("sidecol");
      sidecol.style.maxWidth = 100 - width + "%";
    },
    div_mousedown(event) {
      // get item
      let item = event.target;
      item.style.transition = "initial";
    },
    div_mouseup(event) {
      // get item
      let item = event.target;
      item.style.transition = "";
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
        <v-row class="fill-height" id="viewrow">
          <v-col
            class="ma-0 pa-0 fill-height fill-width"
            id="casecol"
            style="max-width: 70%"
            align="center"
          >
            <CaseNav
              id="case_area"
              :current_case="$route.params.id"
              :refresh_case="refresh_case"
              style="max-width: 100%"
            /> </v-col
          ><v-divider
            id="dragsep"
            @drag="dragged"
            @mousedown="div_mousedown"
            @mouseup="div_mouseup"
            class="ma-0 pa-0"
            vertical
            draggable="true"
          ></v-divider>
          <v-col
            id="sidecol"
            class="ma-0 pa-0"
            align="center"
            style="max-width: 30%"
            width="20%"
          >
            <v-row id="summary" class="ma-0 pa-0 temp" style="height: 40%">
              <v-col align="center"><h4>Document Summary</h4> </v-col
              ><v-card class="p-3 mr-2" elevation="2">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
                enim ad minim veniam, quis nostrud exercitation ullamco laboris
                nisi ut aliquip ex ea commodo consequat.
              </v-card> </v-row
            ><v-divider class="ma-0 pa-0"></v-divider>
            <v-row id="stats" class="ma-0 pa-0 temp" style="height: 30%">
              <v-col align="center"
                ><v-row justify="center" style="height: 30%"
                  ><v-col align="center"><h4>Statistics</h4></v-col> ></v-row
                >
                <v-row justify="center" style="height: 35%"
                  ><v-col align="center"><h6>X% Accuracy</h6></v-col
                  ><v-col align="center"><h6>Best LF: Y</h6></v-col></v-row
                >
                <v-row justify="center" style="height: 35%"
                  ><v-col align="center"><h6>Coverage: Z%</h6></v-col
                  ><v-col align="center"><h6>Stat 4: W%</h6></v-col></v-row
                >
              </v-col>
            </v-row>
            <v-divider class="ma-0 pa-0"></v-divider>
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

#dragsep {
  max-width: 2px;
  color: rgb(0, 0, 0);
}

#dragsep:hover {
  cursor: col-resize;
  // glow
  border: 2px solid rgb(150, 127, 245);
}
.vue-grid-item.cssTransforms {
  transition-property: inherit !important;
}
.vue-resizable.resizing {
  pointer-events: none;
}
.vue-draggable-dragging {
  pointer-events: none;
}

#stats {
  background-color: #1e1e1e;
  color: white;
}
</style>