<template>
    <!-- <div v-if=""></div> -->
    <div class="p-4">
        <ag-grid-vue
        class="ag-theme-alpine"
            style="width: 100%"
            :rowData="rowData"
            :columnDefs="colDefs"
            domLayout="autoHeight"
            v-on:cell-clicked="handleCellClick"
        />
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import axios from 'axios'
import endpoints from "../api/api.js"

const props = defineProps({
    day: {
        type:Number,
        required:true
    },
    location: {
        type:String,
        required:true
    }
});

axios.defaults.withCredentials = true;
const apiBaseUrl = import.meta.env.VITE_BACKEND_DOMAIN;
const fetchGridDataPayload = {
    day: props.day,
    location:props.location
};

const fetchGridDataSuccessful = ref(false);
async function fetchGridData() {
    try {
        const response = await axios.post(apiBaseUrl+endpoints.grid,fetchGridDataPayload);
        const columnDefs = response.data.data.columnDefs;
        const rowData = response.data.data.rowData;
        updateGrid(columnDefs,rowData);
        console.log("Fetch grid data successful");
        fetchGridDataSuccessful.value=true;
    }catch(error) {
        fetchGridDataSuccessful.value=false;
        console.log(`'Grid for ${props.day},${props.location}:'`,error);
    }
}

function updateGrid(newColDefs, newRowData) {
    //update the data of the underlying aggrid
    colDefs.value = newColDefs;
    rowData.value = newRowData;
}

async function handleCellClick(event) {
// console.log(props.day);
    // console.log(props.location);
    // console.log(apiBaseUrl + endpoints.grid);
    await fetchGridData();
};

const rowData = ref([
  { make: 'Tesla', model: 'Model Y', price: 64950, electric: true },
  { make: 'Ford', model: 'F-Series', price: 33850, electric: false },
  { make: 'Toyota', model: 'Corolla', price: 29600, electric: false }
]);

const colDefs = ref([
  { field: 'make' },
  { field: 'model' },
  { field: 'price' },
  { field: 'electric' }
]);
</script>

<style>
.ag-theme-alpine .ag-header-cell {
  border: 1px solid #ccc;
}
</style>
