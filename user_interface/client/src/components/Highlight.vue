<template>
  <div>
    <slot> </slot>
    <div v-html="highlighted"></div>
  </div>
</template>

<script>
export default {
  name: "Highlight",
  props: {
    referenceText: {
      type: Boolean,
      default: false,
    },
  },
  data: () => ({
    selected: "",
    text: "",
    x: 0,
    y: 0,
    highlighted: "",
  }),
  computed: {
    highlightableEl() {
      return this.$slots.default[0].elm;
    },
  },
  methods: {
    test() {
      this.highlighted = this.highlight();
      console.log(this.$slots.default[0].elm);
    },
    copy() {
      return this.highlightableEl === undefined
        ? ""
        : this.highlightableEl.cloneNode();
    },
    onMouseup() {
      try {
        const selection = window.getSelection();
        const selectionRange = selection.getRangeAt(0);

        // if the selected text is not part of the highlightableEl (i.e. <p>)
        // OR
        // if startNode !== endNode (i.e. the user selected multiple paragraphs)
        // Then
        // Don't show the menu (this selection is invalid)

        // Get the x, y, and width of the selection
        const { x, y, width } = selectionRange.getBoundingClientRect();

        // If width === 0 (i.e. no selection)
        // Then, hide the menu
        if (!width) {
          // this.showMenu = false;
          return;
        }

        this.x = x; // + width / 2;
        this.y = y; // + window.scrollY - 10;
        this.selected = selection.toString();
        this.highlight();
      } catch (e) {
        console.log(e);
      }
    },
    strip(html) {
      var doc = new DOMParser().parseFromString(html, "text/html");
      return doc.body.textContent || "";
    },
    highlight() {
      if (this.selected) {
        let text = this.strip(this.selected);

        this.$emit("highlighted", {
          selected: text,
          isReference: this.referenceText,
        });
      }
    },
  },
  mounted() {
    window.addEventListener("mouseup", this.onMouseup);
    this.text = this.$slots.default[0].elm.innerHTML;
  },
  beforeDestroy() {
    window.removeEventListener("mouseup", this.onMouseup);
  },
};
</script>

<style>
.highlightText {
  background-color: yellow;
}
</style>
