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
import { ref} from 'vue';
import { AgGridVue } from 'ag-grid-vue3';
import { useToast } from 'primevue/usetoast';
import axios from 'axios';
import endpoints from "../api/api.js";

const toast = useToast(); // <Toast /> already added on main page

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
const API_BASE_URL = import.meta.env.VITE_BACKEND_DOMAIN;
const GRID_NAME = `DAY${props.day}:${props.location}` ;
const FETCH_GRID_DATA_PAYLOAD = {
    day: props.day,
    location:props.location
};

const fetchGridDataSuccessful = ref(false); // need to add a fetchGridData failed screen
async function fetchGridData() {
    try {
        const response = await axios.post(API_BASE_URL+endpoints.grid,FETCH_GRID_DATA_PAYLOAD);
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
//TODO: Allocate shift, then refresh, need to trigger matching day grids as well
// console.log(props.day);
    // console.log(props.location);
    // console.log(apiBaseUrl + endpoints.grid);
    await fetchGridData();
};

async function addName(name) {
    /**
     * @param {string} name - name of person to add
     */
    // Add name to grid if name does not exist
    try {
        const ADD_NAME_PAYLOAD = {
            "grid_name": GRID_NAME,
            "name": name, 
        };
        const response = await axios.post(API_BASE_URL+endpoints.addName, ADD_NAME_PAYLOAD);
        await fetchGridData();
        toast.add({severity:'info', summary:'Add Name', detail: response.data.detail, life:"4000"});
        console.log(response.data);
    }catch(error) {
        console.log(`'Grid for ${props.day},${props.location}:'`,error);
        toast.add({severity:"error",summary: 'Add Name failed',detail:"Internal Server Error", life:"4000"});
    } 
}

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

defineExpose({ addName });

</script>


<style>
.ag-theme-alpine .ag-header-cell {
  border: 1px solid #ccc;
}
</style>
