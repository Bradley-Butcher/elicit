<template>
  <div>
    <button class="btn">Test</button>
  </div>
  <!-- <Popper>
    <a type="button" class="btn btn-outline-dark btn-sm">Filter</a>
    <template #content>
      <div>
        <h5 style="text-align: center">Filters</h5>
        <div class="dropdown" style="float: left">
          <button
            class="btn btn-secondary btn-sm dropdown-toggle"
            type="button"
            id="dropdownMenuButton1"
            data-bs-toggle="dropdown"
            aria-expanded="false"
            @click="showing = !showing"
            :class="{show : showing}"
          >
            Filters
          </button>
          <ul class="dropdown-menu dropdown-menu-dark" :class="{show : showing}" aria-labelledby="dropdownMenuButton1">
            <li v-for="category in categories" :key="category">
              <a
                class="dropdown-item"
                :class="{active: active_filter == category}"
                @click="active_filter = category"
                href="#"
                >{{ category }}</a
              >
            </li>
          </ul>
        </div>

        <div style="float: right">
          <button
            class="btn btn-secondary align-top btn-sm"
            @click="applyFilter"
          >
            Apply
          </button>
          <button
            class="btn btn-secondary align-top btn-sm"
            @click="resetFilter"
          >
            Reset
          </button>
        </div>
        <div>
          <button class="btn btn-secondary btn-sm" @click="createNewFilter">
            New Filter
          </button>
        </div>
      </div>
    </template>
  </Popper> -->
</template>

<script>
// import Popper from "vue3-popper";

export default {
  components: {
  },
  data() {
    return {
      content: "",
      categories: ["test", "test2"],
      showing: false,
      active_filter: "",
    };
  },
  setup() {
    // $('#filterbutton').popover({
    //     container: 'body'
    // })
  },
};
</script>


<style>
:root {
  --popper-theme-background-color: #e0f5ee;
  --popper-theme-background-color-hover: #ebebeb;
  --popper-theme-text-color: #000000;
  --popper-theme-border-width: 2px;
  --popper-theme-border-style: solid;
  --popper-theme-border-radius: 6px;
  --popper-theme-padding: 32px;
  --popper-theme-box-shadow: 0 6px 30px -6px rgba(0, 0, 0, 0.25);
}
</style>