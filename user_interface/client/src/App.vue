<script>
import CaseNav from "./components/CaseNav.vue";
import CaseMenu from "./components/CaseMenu.vue";
import TrainButton from "./components/TrainButton.vue";
import Filter from "./components/Filter.vue";
import Export from "./components/Export.vue";

export default {
  name: "App",
  components: {
    CaseNav,
    CaseMenu,
    TrainButton,
    Filter,
    Export
  },
  data() {
    return {
      active_case: "",
      refresh_case: 0,
    };
  },
  methods: {
    onCaseClicked(value) {
      this.active_case = value;
    },
    updateCase() {
      
    }
  },
};
</script>

<template>
  <div id="app">
    <div id="modals"></div>
    <CaseMenu @clicked="onCaseClicked" style="float: left" />
    <nav id="main_nav" class="navbar navbar-light bg-light">
      <div class="container-fluid">
        <img
          src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Alan_Turing_Institute_logo.svg/1200px-Alan_Turing_Institute_logo.svg.png"
          alt=""
          width="70"
          height="30"
          class="me-100"
        />
        <a class="navbar-brand text-black"><img src="./assets/elecit.png" style="height:35px;"></a>
        <ul class="navbar-nav">

        <div class="d-flex" style="width:200px">
          <li class="nav-item me-2">
          <Filter class="float-right"/>
          </li>
          <li class="nav-item me-2">
          <TrainButton @retrained="refresh_case+=1" class="float-left"/>
          </li>
          <li class="nav-item">
          <Export class="float-right"/>
          </li>
        </div>
        </ul>
      </div>
    </nav>
    <CaseNav
      id="case_area"
      class="d-flex flex-column flex-grow-1"
      :current_case="active_case"
      :refresh_case="refresh_case"
      style="margin-top: 2%"
    />
    <router-view />
  </div>
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
</style>