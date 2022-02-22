<script>
import CaseNav from "../components/CaseNav.vue";

export default {
  name: "CaseView",
  components: {
    CaseNav
  },
  data() {
    return {
      active_case: this.$route.params.id,
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
  <div>
    <CaseNav
      id="case_area"
      class="d-flex flex-column flex-grow-1"
      :current_case="$route.params.id"
      :refresh_case="refresh_case"
      style="margin-top: 2%"
    />
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