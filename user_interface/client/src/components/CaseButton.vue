<template>
  <div>
    <h2 class="accordion-header">
      <button
        class="accordion-button"
        :class="[{ collapsed: active == false }]"
        type="button"
        :data-bs-toggle="target"
        data-bs-target="#collapse"
        aria-expanded="false"
        :aria-controls="target"
        @click="emit_click"
      >
        <slot> </slot>
        <div class="options ms-auto">
          <v-card
            class="p-1"
            :class="{
              answered: status && status != 'null',
              unanswered: !status || status == 'null',
            }"
            :elevation="status ? 1 : 0"
            outlined
            tile
            disabled
          >
            <div>validated</div>
          </v-card>
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
    active: {
      type: Boolean,
      required: true,
    },
    status: {
      required: true,
    },
  },
  methods: {
    emit_click() {
      this.$emit("tabclick", this.target);
    },
    send_signal(signal_type) {
      if (signal_type == this.status) {
        this.$emit("signal", [this.target_id, this.target, null]);
        this.status = null;
      } else {
        this.$emit("signal", [this.target_id, this.target, signal_type]);
      }
    },
  },
};
</script>

<style scoped>
.options i {
  padding: 10px;
}

.options i:hover {
  color: rgb(104, 211, 5);
}

.selected_option {
  color: rgb(104, 211, 5);
}

.unanswered {
  background-color: #ffffff;
  color: #000000;
  text-decoration: line-through;
}

.answered {
  background-color: #4caf50;
  color: #150000;
  text-decoration: none;
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
  background-color: #2f3e46;
  color: white;
}

.accordion-button:focus {
  outline: none !important;
  box-shadow: none;
}
</style>