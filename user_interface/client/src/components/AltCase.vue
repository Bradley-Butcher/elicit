

<script>
import CaseButton from "./CaseButton.vue";
import ContextModal from "./ContextModal.vue";
import axios from "axios";

export default {
  name: "App",
  components: {
    CaseButton,
    ContextModal
  },
  data() {
    return {
      showModalNow: false,
      active_evidence: {},
      extracted_data: {},
      active_field_value: "",
      active_tab: -1,
      toast_showing: false,
      toast_text: "",
      toast_title: "",
      renderComponent: true,
    };
  },
  props: {
    variable: {
      type: String,
      required: true,
    },
    variable_data: {
      type: Object,
      required: true,
    },
  },
  watch : {
    variable_data() {
      this.getCase();
    }
  },
  computed: {
    sorted_variable_data() {
      let sorted_variables = {};
      for(let i = 0; i < this.variable_data.length; i++) {
        let datum = this.variable_data[i];
        if(datum.confidence) {
          sorted_variables[datum.confidence] = datum;
        } else {
          sorted_variables[this.get_total_confidence(this.extracted_data, datum.variable_id)] = datum;
        }
      }
      console.log(sorted_variables);
      // return sorted list
      return Object.keys(sorted_variables).sort().reverse().map(function(key) {
        return sorted_variables[key];
      });
    }
  },
  methods: {
    setEvidence(evidence) {
      this.active_evidence = evidence;
      this.showModalNow = !this.showModalNow;
    },
    setExtraction(extraction) {
      this.active_field_value = extraction;
      this.showModalNow = !this.showModalNow;
    },
    getIds(data) {
      let ids = [];
      data.forEach((estimate) => {
        var idSet = [estimate["document_id"], estimate["variable_id"]];
        ids.push(idSet);
      });
      return ids;
    },
    getCase() {
      const path = "http://127.0.0.1:5000/api/case_evidence/" + this.getIds(this.variable_data);
      axios
        .get(path)
        .then((res) => {
          this.extracted_data = res.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    setAnswer(variable_id, answer) {
      const path = "http://127.0.0.1:5000/api/submit_answer/" + variable_id + "/" + answer;
      axios
        .post(path)
        .then(() => {
          this.$emit("reload_variable");
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    closeModalNow() {
      this.showModalNow = false;
    },
    getTarget(id) {
      return `'collapse-${id}'`;
    },
    triggerTab(tab_id) {
      if (this.active_tab == tab_id) {
        this.active_tab = -1;
      } else {
        this.active_tab = tab_id;
      }
    },
    format_evidence(input_data, variable_id) {
      let data = [];
      for (const i in input_data) {
        if (input_data[i].variable_id == variable_id) {
          data.push(input_data[i]);
        }
      }
      return data
    },
    get_agreement(input_data, variable_id) {
      let agreement_count = 0;
      let total_count = 0;
      for (const i in input_data) {
        if (input_data[i].variable_id == variable_id) {
          if(input_data[i].confidence > 0) {
            agreement_count += 1;
          }
          total_count += 1;
        }
      }
      return "Agreement: " + agreement_count + " / " + total_count;
    },
    get_total_confidence(input_data, variable_id) {
      let total_count = 0;
      for (const i in input_data) {
        if (input_data[i].variable_id == variable_id) {
          total_count += parseFloat(input_data[i].confidence);
        }
      }
      return total_count;
    },
    get_confidence(var_data, input_data, variable_id) {
      if (!var_data.confidence) {
        return this.get_agreement(input_data, variable_id);
      } else {
        return "Confidence: " + Number( Number(var_data.confidence * 100).toPrecision(4) ) + "%";
      }
    },
    get_best_evidence(item) {
      //Change to use some "best evidence variable" and "exact context "
      const ev = this.format_evidence(this.extracted_data, item.variable_id)
      const best_ev = ev.sort((a, b) => {
        return b.confidence - a.confidence;
      })[0];
      if (best_ev && best_ev.exact_context) {
        // get exact context split by commas, newlines or periods. Return first.
        const context = best_ev.exact_context.split(/[,\n.]/);
        return '"' + context[0] + '"';
      } else {
        return "No Evidence";
      }
    },
    add_mark(evidence) {
      // replace text substr with <mark>substr</mark>
      if (!evidence.exact_context) {
        return "No Evidence";
      }
      if (evidence.exact_context == "N/A") {
        return evidence.exact_context;
      }
      let substr = evidence.exact_context;
      let regex = new RegExp(substr, "gi");
      let new_text = evidence.local_context.replace(regex, "<mark>" + substr + "</mark>");
      return new_text;
    },
    show_toast(text) {
      this.toast_showing = true;
      this.toast_text = text;
      setTimeout(() => {
        this.toast_showing = false;
      }, 3000);
    },
    collect_answer(args) {
      const subject_id = args[0];
      const subject = args[1];
      const answer = args[2];
      this.setAnswer(subject_id, answer);
      this.active_tab = -1;
      this.show_toast(
        "<span><strong>" +
          subject +
          "</strong> set as: <strong>" +
          answer +
          "</strong> for variable: <strong>" +
          this.variable +
          "</strong></span>"
      );
    },
  },
};
</script>

<template>
  <div>
    <div class="accordion" id="caseAccordian">
      <div
        class="accordion-item"
        v-for="varz in sorted_variable_data" :key="varz.variable_id"
        :id="varz.variable_id"
      >
        <CaseButton
          :target="varz.variable_value"
          :target_id="varz.variable_id"
          @tabclick="triggerTab"
          :active="varz.variable_value == active_tab"
          :status="varz.human_response"
          @signal="collect_answer"
          v-if="renderComponent"
        >
          <div class="p-2 bg-primary text-white">Value: {{ varz.variable_value }}</div>
          <div class="vr bg-dark"></div>
          <div class="p-2 bg-secondary text-white">
            <!-- {{ varz.confidence }} -->
            {{ get_confidence(varz, extracted_data, varz.variable_id) }}
          </div>
          <div class="vr bg-dark"></div>
          <div class="p-2 bg-warning text-white" style="max-width:50%;">
            Evidence: {{ get_best_evidence(varz) }}
          </div>
        </CaseButton>

        <div
          id="collapseOne"
          class="accordion-collapse collapse"
          :class="{ show: active_tab == varz.variable_value }"
          aria-labelledby="headingOne"
          data-bs-parent="#accordionExample"
        >
          <div class="accordion-body">
            <div class="table-responsive">
              <table id="var_table" class="table justify-content-center">
                <thead>
                  <tr>
                    <th style="width: 40%" scope="col">Evidence</th>
                    <th style="width: 20%" scope="col">Source</th>
                    <th style="width: 20%" scope="col">Confidence</th>
                    <th style="width: 20%" scope="col">More Context</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="ev in format_evidence(extracted_data, varz.variable_id)" :key="ev">
                    <th scope="row">
                      <span v-html="add_mark(ev)"></span>
                    </th>
                    <td>{{ ev.method }}</td>
                    <td>{{ Math.round(ev.confidence * 1000) / 10 }}%</td>
                    <td><button class="btn btn-secondary btn-sm mx-auto" @click="setEvidence(ev)">View</button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">
      <div
        id="liveToast"
        class="toast align-items-center fade"
        :class="{ hide: toast_showing == false, show: toast_showing == true }"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
      >
        <div class="d-flex bg-dark text-white">
          <div class="toast-body bg-dark text-white" v-html="toast_text"></div>
          <button
            type="button"
            class="btn-close me-2 m-auto text-white"
            data-bs-dismiss="toast"
            aria-label="Close"
            @click="hide_toast"
          ></button>
        </div>
      </div>
    </div>
    <ContextModal :evidence="active_evidence" :showModal="showModalNow" @closeModal="closeModalNow"></ContextModal>
  </div>
</template>

<style>
@import "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css";
#var_table {
  margin-left: auto;
  margin-right: auto;
  margin-top: 2%;
}
#variable_title {
  margin-left: auto;
  margin-right: auto;
  margin-top: 2%;
}
</style>