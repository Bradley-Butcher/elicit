

<script>
import CaseButton from "./CaseButton.vue";
import ContextModal from "./ContextModal.vue";
import axios from "axios";

export default {
  name: "Extractions",
  components: {
    CaseButton,
    ContextModal,
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
      type: Array,
      required: true,
    },
  },
  watch: {
    variable_data() {
      this.getCase();
    },
  },
  methods: {
    variable_status(evidence_list) {
      for (var i = 0; i < evidence_list.length; i++) {
        if (evidence_list[i].valid == "TRUE") {
          return true;
        }
      }
      return false;
    },
    sort_var_data(variable_data, extracted_data) {
      for (let i = 0; i < variable_data.length; i++) {
        if (variable_data[i].confidence == null) {
          variable_data[i].temp_confidence = this.get_total_confidence(
            extracted_data,
            variable_data[i].variable_id
          );
        }
      }
      // sort by confidence, then by temp_confidence, then by variable_name
      variable_data.sort((a, b) =>
        a.confidence < b.confidence
          ? 1
          : a.confidence === b.confidence
          ? a.temp_confidence < b.temp_confidence
            ? 1
            : a.temp_confidence === b.temp_confidence ||
              a.temp_confidence == 0 ||
              b.temp_confidence == 0
            ? a.variable_name < b.variable_name
              ? 1
              : -1
            : -1
          : -1
      );
      return variable_data;
    },
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
      const path =
        "http://127.0.0.1:5000/api/case_evidence/" +
        this.getIds(this.variable_data);
      axios
        .get(path)
        .then((res) => {
          this.extracted_data = res.data;
          this.variable_data = this.sort_var_data(
            this.variable_data,
            this.extracted_data
          );
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    setAnswer(extraction_id, answer) {
      const path =
        "http://127.0.0.1:5000/api/submit_answer/" +
        extraction_id +
        "/" +
        answer;
      axios
        .post(path)
        .then(() => {
          // this.$emit("reload_variable");
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
      // sort by confidence
      data.sort((a, b) => (a.confidence < b.confidence ? 1 : -1));
      return data;
    },
    get_agreement(input_data, variable_id) {
      let agreement_count = 0;
      let total_count = 0;
      for (const i in input_data) {
        if (input_data[i].variable_id == variable_id) {
          if (input_data[i].confidence > 0) {
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
          if (input_data[i].confidence > 0) {
            total_count += 1;
          }
        }
      }
      return total_count;
    },
    get_confidence(var_data, input_data, variable_id) {
      if (!var_data.confidence) {
        return this.get_agreement(input_data, variable_id);
      } else {
        return (
          "Confidence: " +
          Number(Number(var_data.confidence * 100).toPrecision(4)) +
          "%"
        );
      }
    },
    get_best_evidence(item) {
      //Change to use some "best evidence variable" and "exact context "
      const ev = this.format_evidence(this.extracted_data, item.variable_id);
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
      let new_text = evidence.local_context.replace(
        regex,
        "<mark>" + substr + "</mark>"
      );
      return new_text;
    },
    show_toast(text) {
      this.toast_showing = true;
      this.toast_text = text;
      setTimeout(() => {
        this.toast_showing = false;
      }, 5000);
    },
    collect_answer(variable, extraction, answer) {
      if (extraction.valid != answer) {
        extraction.valid = answer;
      } else {
        extraction.valid = null;
      }
      this.setAnswer(extraction.extraction_id, extraction.valid);
      this.show_toast(
        "<span>Evidence from: <strong>" +
          extraction.method +
          "</strong> for value: <strong>" +
          variable.variable_value +
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
  <div style="max-height: 1000px">
    <div class="accordion accordion-flush" id="caseAccordian">
      <div
        class="accordion-item"
        v-for="varz in variable_data"
        :key="varz.variable_id"
        :id="varz.variable_id"
      >
        <CaseButton
          :target="varz.variable_value"
          :target_id="varz.variable_id"
          @tabclick="triggerTab(varz.variable_id)"
          :active="varz.variable_value == active_tab"
          :status="
            variable_status(format_evidence(extracted_data, varz.variable_id))
          "
          v-if="renderComponent"
        >
          <v-card
            class="p-2 mr-2"
            elevation="0"
            outlined
            style="background-color: #f9fbe7"
          >
            <div class="text-black">Value: {{ varz.variable_value }}</div>
          </v-card>
          <v-card
            class="p-2 mr-2"
            elevation="0"
            outlined
            style="background-color: #f3e5f5"
          >
            <div class="text-black">
              <!-- {{ varz.confidence }} -->
              {{ get_confidence(varz, extracted_data, varz.variable_id) }}
            </div></v-card
          >
          <v-card
            class="p-2"
            elevation="0"
            outlined
            style="background-color: #eceff1"
          >
            <div class="text-black" style="max-width: 100%">
              Evidence: {{ get_best_evidence(varz) }}
            </div></v-card
          >
        </CaseButton>

        <div
          id="collapseOne"
          class="accordion-collapse collapse"
          :class="{ show: active_tab == varz.variable_id }"
          aria-labelledby="headingOne"
          data-bs-parent="#accordionExample"
        >
          <div class="accordion-body">
            <div class="table-responsive">
              <table id="var_table" class="table justify-content-center">
                <thead>
                  <tr>
                    <th style="max-width: 40%" scope="col">Evidence</th>
                    <th style="max-width: 15%; text-align: center" scope="col">
                      Source
                    </th>
                    <th style="max-width: 15%; text-align: center" scope="col">
                      Confidence
                    </th>
                    <th style="max-width: 15%; text-align: center" scope="col">
                      Context
                    </th>
                    <th style="max-width: 15%; text-align: center" scope="col">
                      Valid
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="ev in format_evidence(
                      extracted_data,
                      varz.variable_id
                    )"
                    :key="ev.id"
                  >
                    <th scope="row">
                      <span v-html="add_mark(ev)"></span>
                    </th>
                    <td style="text-align: center">{{ ev.method }}</td>
                    <td style="text-align: center">
                      {{ Math.round(ev.confidence * 1000) / 10 }}%
                    </td>
                    <td style="text-align: center">
                      <v-btn
                        class="p-0"
                        depressed
                        outlined
                        small
                        @click="setEvidence(ev)"
                        >View</v-btn
                      >
                    </td>
                    <td style="text-align: center">
                      <i
                        @click="collect_answer(varz, ev, 'TRUE')"
                        class="fas fa-check fa-lg ms-auto check mr-1"
                        :class="{ valid: ev.valid == 'TRUE' }"
                      ></i>
                      <i
                        @click="collect_answer(varz, ev, 'FALSE')"
                        class="fas fa-times fa-lg ms-auto check ml-1"
                        :class="{ valid: ev.valid == 'FALSE' }"
                      ></i>
                    </td>
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
          ></button>
        </div>
      </div>
    </div>
    <ContextModal
      :evidence="active_evidence"
      :showModal="showModalNow"
      @closeModal="closeModalNow"
    ></ContextModal>
  </div>
</template>

<style>
@import "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css";

#var_table {
  margin-left: auto;
  margin-right: auto;
  margin-top: 1%;
  margin-bottom: 0;
}

#variable_title {
  margin-left: auto;
  margin-right: auto;
  margin-top: 2%;
}

.accordion-body {
  /* only padding left 10px */
  padding: 0 20px 0 30px;
}

.table > :not(:first-child) {
  border-top: none;
}

.check:hover {
  color: rgb(104, 211, 5);
  cursor: pointer;
}

.valid {
  color: rgb(104, 211, 5);
}
</style>