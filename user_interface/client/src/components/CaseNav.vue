<template>
  <div class="ma-0 pa-0 ml-2">
    <v-tabs background-color="#FFF" color="black" show-arrows full-width>
      <v-tab
        :class="{
          'v-tab--active': val == active_variable,
          processed: getStatus(val),
        }"
        v-for="val in variables"
        :key="val"
        :href="'#tab-' + val"
        @click="active_variable = val"
        >{{ val.replace(/_/g, " ") }}</v-tab
      >
    </v-tabs>
    <!-- <AltCase
      :variable="active_variable"
      :variable_data="active_variable_data"
      :training_state="training_state"
      @reload_variable="getMessage"
    /> -->
    <CategoryList
      :document_name="document_id"
      :variable_name="active_variable"
    ></CategoryList>
  </div>
</template>

<script>
import axios from "axios";
import CategoryList from "./extraction_components/CategoryList.vue";

export default {
  name: "CaseNav",
  props: ["document_id", "refresh_case", "training_state"],
  components: {
    CategoryList,
  },
  data() {
    return {
      variable_list: [],
      active_variable: "",
    };
  },
  watch: {
    document_id() {
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
        "http://127.0.0.1:5000/api/case_variables/" + this.document_id;
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
    document_title() {
      let repl_str = this.document_id.replace(/_/g, " ");
      return repl_str;
    },
  },
  mounted() {
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