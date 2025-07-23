<template>
    <!-- <div v-if=""></div> -->
    <div class="p-4">
        <ag-grid-vue
        class="ag-theme-alpine"
            style="width: 100%"
            :rowData="rowData"
            :columnDefs="colDefs"
            domLayout="autoHeight"
            
            @cell-clicked="handleCellClick"
        />
    </div>
</template>

<script setup>
import { onMounted, ref} from 'vue';
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
    },
    selectedLocation : { // passed in from radio button ref
        type:String,
        required:true
    },
    selectedShiftSize: { // passed in from radio button ref
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

    //map cell class rules to columnDefs

    addCellClassRules(newColDefs);
    colDefs.value = newColDefs;
    rowData.value = newRowData;
}

function addCellClassRules(colDefs) {
  colDefs.forEach(colDef => {
    if (colDef.field !== 'DAY1:MCC') { //skip first col
      colDef.cellClassRules = {
        'bg-white text-white': params => params.value === "0",
        'bg-green text-green': params => params.value === props.location,
        'bg-green text-black': params => params.value !== "0" && params.value !== props.location,
      };
    }
  });
}

async function handleCellClick(params) {
    const ALLOCATE_SHIFT_PAYLOAD = {
        "grid_name" : GRID_NAME,
        "name": params.data[GRID_NAME],
        "location": props.selectedLocation,
        "time_block": params.column.getColId(),
        "allocation_size": props.selectedShiftSize
    };
    console.log(ALLOCATE_SHIFT_PAYLOAD);
    try {
        const response = await axios.post(API_BASE_URL+endpoints.allocateShift,ALLOCATE_SHIFT_PAYLOAD);
        await fetchGridData();
    } catch(error) {
        toast.add({severity:"error",summary: 'Add Name failed',detail:"Internal Server Error", life:"4000"}); 
        console.log(`Grid for ${props.day},${props.location}:`,error);
    }
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
        toast.add({severity:"error",summary: 'Add Name failed',detail:"Internal Server Error", life:"4000"});
        console.log(`Grid for ${props.day},${props.location}:`,error);
    } 
}

async function removeName(name) {
    try {
        const REMOVE_NAME_PAYLOAD = {
            "grid_name":GRID_NAME,
            "name":name,
        }
        const response = await axios.delete(API_BASE_URL + endpoints.removeName, {data:REMOVE_NAME_PAYLOAD});
        await fetchGridData();
        toast.add({severity:'info', summary:'Remove Name', detail: response.data.detail, life:"4000"});
        console.log(response.data);
        
    } catch(error) {
        toast.add({severity:"error", summary:'Remove Name Failed', detail:"Internal Server Eror", life:"4000"});
        console.log(`Grid for ${props.day}, ${props.location}:`, error);
    }
}

onMounted(async () => {
    await fetchGridData();
})
const rowData = ref([]);
const colDefs = ref([]);

defineExpose({ addName, removeName});

</script>


<style>
/* Header cells */
.ag-theme-alpine .ag-header-cell {
  border: 1px solid #ccc;
}

/* Data cells */
.ag-theme-alpine .ag-cell {
  border: 1px solid #ccc;
  transition: border 0.3s ease, box-shadow 0.3s ease;
}
/* On hover change border to blue */
.ag-theme-alpine .ag-cell:hover {
  border: 1px solid #0768fa;
  box-shadow: 0 0 4px rgba(150, 150, 200, 0.3);
  z-index: 1;
}

.bg-white {
  background-color: white;
}

.text-white {
  color: white;
}

.bg-green {
  background-color: rgb(0, 190, 0);
}

.text-green {
  color: rgb(0, 190, 0);
}

.text-black {
  color: black;
}

</style>
