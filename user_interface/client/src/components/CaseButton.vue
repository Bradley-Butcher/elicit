<template>
  <div>
    <h2 class="accordion-header">
      <button
        class="accordion-button"
        :class="[{ collapsed: active == false }, {answered: status}]"
        type="button"
        :data-bs-toggle="target"
        data-bs-target="#collapse"
        aria-expanded="false"
        :aria-controls="target"
        @click="emit_click"
      >
        <slot> </slot>
        <div class="options ms-auto">
          <i @click.stop="send_signal('correct')" v-bind:class="{selected_option: status == `correct`}" class="fas fa-check fa-lg"></i>
          <i @click.stop="send_signal('unknown')" v-bind:class="{selected_option: status == `unknown`}" class="fas fa-question fa-lg"></i>
          <i @click.stop="send_signal('incorrect')" v-bind:class="{selected_option: status == `incorrect`}" class="fas fa-times fa-lg"></i>
        </div>
      </button>
    </h2>
  </div>
</template>

<script>
export default {
  name: "CaseButton",
  props: {
    target: {
      type: String,
      required: true,
    },
    target_id: {
      type: Number,
      required: true,
    },
    active : {
        type: Boolean,
        required: true,
    },
    status: {
      required: true,
    }
  },
  methods: {
    emit_click() {
      this.$emit("tabclick", this.target);
    },
    send_signal(signal_type) {
      if (signal_type == this.status) {
        this.$emit("signal", [this.target_id, this.target, null]);
      } else {
        this.$emit("signal", [this.target_id, this.target, signal_type]);
      }
    }
  },
};
</script>

<style scoped>

.options i{
  padding: 10px;
}

.options i:hover{
  color: rgb(104, 211, 5);
}

.selected_option {
  color: rgb(104, 211, 5);
}

.answered {
  background-color: rgba(161, 163, 159, 0.185);
}

.accordion-button:not(.collapsed)::after {
    background-image: url("https://icons.getbootstrap.com/assets/icons/chevron-down.svg");
    filter: invert(100%);
    transform: rotate(-180deg);
}

.accordion-button::after {
    margin-left: 2%;
    color: white;
}

.accordion-button:not(.collapsed) {
    background-color: #2a2a2e;
    color: white;
}

.accordion-button:focus{
   outline: none !important;
   box-shadow: none;
}




</style>