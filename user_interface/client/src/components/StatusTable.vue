<template>
  <v-card>
    <v-card-title>
      <v-text-field
        v-model="search"
        append-icon="mdi-magnify"
        label="Search"
        single-line
        hide-details
      ></v-text-field>
    </v-card-title>
    <v-data-table
      :headers="columns"
      :items="rows"
      :search="search"
      @click:row="rowClick"
      @current-items="currentItems"
      disable-sort
    >
    <template v-for="slot in variables" v-slot:[slot.appended_name]="{ item }">
      <v-chip
        :key="slot.name"
        label
        :border-radius-root="0"
        :class="{'true-chip': item[slot.name] === true, 'false-chip': item[slot.name] === false}"
      >
        <v-icon v-if="item[slot.name] === true">mdi-check</v-icon>
        <v-icon v-if="item[slot.name] === false">mdi-close</v-icon>
      </v-chip>
    </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios";

export default {
  name: "StatusTable",
  data() {
    return {
        rows: [],
        columns: [],
        variables: [],
        search: '',
    };
  },
  methods: {
    create_columns(keys) {
        let columns = [];
        for (let i = 0; i < keys.length; i++) {
            columns.push({
            value: keys[i],
            // title case and replace _ with space
            text: keys[i].replace(/_/g, " ").replace(/\w\S*/g, function (txt) {
                return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
            }),
            filterable: true,
            });
        }
        return columns;
    },
    rowClick(item) {
        this.$router.push({
            name: "Document",
            params: {
                id: item.document_name,
            },
        });
    },
    sortRows(rows, document_order) {
        let sorted_rows = [];
        console.log(document_order);
        for (let i = 0; i < document_order.length; i++) {
            for (let j = 0; j < rows.length; j++) {
                if (document_order[i].case_id === rows[j].document_name) {
                    sorted_rows.push(rows[j]);
                }
            }
        }
        return sorted_rows;
    },
    currentItems: function(value){
      this.itemsPerPage = -1
      console.log(value)
    },
    get_documents() {
      const path = "http://127.0.0.1:5000/api/get_document_status";
      axios
        .get(path)
        .then((res) => {
            this.rows = this.sortRows(JSON.parse(res.data), this.document_list);
            this.columns = this.create_columns(Object.keys(this.rows[0]));
            // {id: 0, appended_name:"item.offenses", name: "offenses"} for each key
            this.variables = this.columns.map((column) => {
                return {
                appended_name: "item." + column.value,
                name: column.value,
                };
            });
            // remove first item from variables
            this.variables.shift();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  props: {
    document_list: {
      type: Array,
    },
  },
  created() {
    this.get_documents();
  },
  watch : {
    document_list: function (new_value) {
        this.rows = this.sortRows(this.rows, new_value);
    },
  },
  components: {
  },
};
</script>

<style scoped>
.true-chip {
  background-color: #1EB980 !important;
}
.false-chip {
  background-color: #F44336 !important;
}
</style>