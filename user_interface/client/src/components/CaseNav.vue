<template>
  <div class="ma-0 pa-0">
    <v-tabs background-color="#2a2a2e" color="white" dark show-arrows full-width>
      <v-tab :class="{
        'v-tab--active': val == active_variable,
        processed: getStatus(val),
      }" v-for="val in variables" :key="val" :href="'#tab-' + val" @click="active_variable = val">{{ val.replace(/_/g, " ") }}</v-tab>
    </v-tabs>
    <AltCase :variable="active_variable" :variable_data="active_variable_data" @reload_variable="getMessage" />
  </div>
</template>

<script>
import axios from "axios";
import AltCase from "./AltCase.vue";

export default {
  name: "CaseNav",
  props: ["current_case", "refresh_case"],
  components: {
    AltCase,
  },
  data() {
    return {
      variable_list: [],
      active_variable: "",
    };
  },
  watch: {
    current_case() {
      this.getMessage();
    },
    refresh_case() {
      this.getMessage();
    },
  },
  methods: {
    updateCase() {
      this.getMessage();
    },
    getMessage() {
      const path =
        "http://127.0.0.1:5000/api/case_variables/" + this.current_case;
      axios
        .get(path)
        .then((res) => {
          // replace _ with spaces in the variable names
          this.variable_list = res.data;
          if (!this.active_variable) {
            let first_key = res.data[0]["variable_name"];
            this.active_variable = first_key;
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    getStatus(variable_name) {
      let count = 0;
      for (let i = 0; i < this.variable_list.length; i++) {
        let key = this.variable_list[i];
        if (key.variable_name == variable_name && key.human_response) {
          count += 1;
        }
      }
      if (count == 0) {
        return false;
      } else {
        return true;
      }
    },
  },
  computed: {
    variables() {
      // iterate over list
      let variables = [];
      for (let i = 0; i < this.variable_list.length; i++) {
        let key = this.variable_list[i]["variable_name"];
        if (variables.indexOf(key) == -1) {
          // replace _ with spaces
          variables.push(key);
        }
      }
      return variables;
    },
    active_variable_data() {
      let data = [];
      for (let i = 0; i < this.variable_list.length; i++) {
        let key = this.variable_list[i]["variable_name"];
        if (key == this.active_variable) {
          data.push(this.variable_list[i]);
        }
      }
      return data;
    },
    case_title() {
      let repl_str = this.current_case.replace(/_/g, " ");
      return repl_str;
    },
  },
  created() {
    this.getMessage();
  },
};
</script>

<style scoped>
#field_nav {
  margin-top: 3%;
}

.partial {
  border-bottom: 2px solid #ffc10796 !important;
}

.complete {
  border-bottom: 2px solid #28a746a1 !important;
}

.active {
  border-bottom: 2px solid #000000 !important;
}

.title_thing {
  display: inline;
}

.processed {
  color: #7ba786 !important;
}
</style>