<template>
    <div>
        <div>
            <p> Filters: </p>
              <div class="dropdown-menu" v-for="category in categories" :key="category">
                <a class="dropdown-item" href="#" @click="filterClick(category)">{{category}}</a>
            </div>
            <button @click="applyFilter"> Apply </button>
            <button @click="resetFilter"> Reset </button>
        </div>
        <div>
            <button @click="createNewFilter"> New Filter </button>
        </div>
    </div>
</template>

<script>
export default {
    setup() {
        
    },
}
</script>