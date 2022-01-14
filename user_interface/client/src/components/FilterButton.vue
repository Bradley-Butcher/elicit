<template>
    <button id="filterbutton" class="btn btn-secondary btn-sm" data-container="body" data-toggle="popover" data-placement="bottom" data-html="true" data-content="<FilterUI></FilterUI>">Filter</button>
</template>

<script>

export default ({
    data() {
        return {
            content: "",
        }
    }
})
</script>
