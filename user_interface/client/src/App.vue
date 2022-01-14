<script>
import CaseNav from "./components/CaseNav.vue";
import CaseMenu from "./components/CaseMenu.vue";
import TrainButton from "./components/TrainButton.vue";
import FilterButton from "./components/FilterButton.vue";

export default {
  name: "App",
  components: {
    CaseNav,
    CaseMenu,
    TrainButton,
    FilterButton
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
    <nav id="main_nav" class="navbar navbar-light bg-light text-end">
      <div class="container-fluid text-end">
        <img
          src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Alan_Turing_Institute_logo.svg/1200px-Alan_Turing_Institute_logo.svg.png"
          alt=""
          width="70"
          height="30"
        />
        <a class="navbar-brand text-black"><img src="./assets/elecit.png" style="height:35px;"></a>
        <div class="d-block float-right">
          <FilterButton class="float-right" style="margin-right:10px;"/>
          <TrainButton @retrained="refresh_case+=1" class="float-left"/>
        </div>
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