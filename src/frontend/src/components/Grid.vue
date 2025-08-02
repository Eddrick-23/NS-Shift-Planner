<template>
    <div v-if="!fetchGridDataSuccessful" class="w-full flex flex-col text-center justify-center">
        <p style="color: red">Unable to fetch grid data</p>
    </div>
    <div v-else-if="props.location === 'HCC2' && rowData && rowData.length > 0" class="ml-6 mr-2 mb-1">
        <ag-grid-vue
            class="customGrid"
            :theme="myTheme"
            style="width: 100%"
            dom-layout="autoHeight"
            :row-height="30"
            :header-height="30"
            :rowData="rowData"
            :columnDefs="colDefs"
            @cell-clicked="handleCellClick"
        />
    </div>
    <div v-else-if="props.location !== 'HCC2'" class="ml-6 mr-2 mb-1">
        <ag-grid-vue
            class="customGrid"
            :theme="myTheme"
            style="width: 100%"
            dom-layout="autoHeight"
            :row-height="30"
            :header-height="30"
            :rowData="rowData"
            :columnDefs="colDefs"
            @cell-clicked="handleCellClick"
        />
    </div>
</template>

<script setup>
import { onMounted, ref, computed, registerRuntimeCompiler} from 'vue';
import { AgGridVue } from 'ag-grid-vue3';
import {themeQuartz, colorSchemeLightCold} from 'ag-grid-community'; 
import { useToast } from 'primevue/usetoast';
import axios from 'axios';
import endpoints from "../api/api.js";

const myTheme = themeQuartz.withParams({
    fontFamily: 'sans-serif',
    headerColumnBorder:{style:'solid',width:"1px"},
    headerRowBorder: {style:'solid',width:"1px"},
    rowBorder: { style: 'solid',width:"1.5px"},
    columnBorder: { style: 'solid',width:"1.5px"}, 

}).withPart(colorSchemeLightCold);


const toast = useToast(); // <Toast /> already added on main page
const emit = defineEmits(['shift-allocated']);
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
const disableCellClicks = ref(false);

const fetchGridDataSuccessful = ref(true);
async function fetchGridData(url = '') { //pass in optional url for compressed grid format
    try {
        const finalUrl = url === '' ? API_BASE_URL + endpoints.grid : url;
        const response = await axios.post(finalUrl,FETCH_GRID_DATA_PAYLOAD);
        const columnDefs = response.data.data.columnDefs;
        const rowData = response.data.data.rowData;
        updateGrid(columnDefs,rowData);
        console.log("Fetch grid data successful");
        fetchGridDataSuccessful.value=true;
    }catch(error) {
        fetchGridDataSuccessful.value=false;
        if (error.response) {
            console.error(`Grid fetch failed for ${props.day}, ${props.location}:`);
            console.error('Status:', error.response.status);
            console.error('Status Text:', error.response.statusText);
            console.error('Response Data:', error.response.data);
            console.error('Response Headers:', error.response.headers);
        } else if (error.request) {
            console.error(`Network error for ${props.day}, ${props.location}:`, error.message);
            console.error('Request:', error.request);
        } else {
            console.error(`Grid fetch error for ${props.day}, ${props.location}:`, error.message);
        } 
        console.error(`'Grid for ${props.day},${props.location}:'`,error);
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
    if (colDef.field !== GRID_NAME) { //skip first col
      colDef.cellClassRules = {
        'bg-white text-white': params => params.value === "0",
        'bg-green text-green': params => params.value === props.location,
        'bg-green text-black': params => params.value !== "0" && params.value !== props.location,
      };
    }
  });
}

async function handleCellClick(params) {
    if (disableCellClicks.value === true) {
        toast.add({severity:'info', summary: 'Clicks disabled',life:'4000'});
        return;
    }
    const ALLOCATE_SHIFT_PAYLOAD = {
        "grid_name" : GRID_NAME,
        "name": params.data[GRID_NAME],
        "location": props.selectedLocation,
        "time_block": params.column.getColId(),
        "allocation_size": props.selectedShiftSize
    };
    try {
        const response = await axios.post(API_BASE_URL+endpoints.allocateShift,ALLOCATE_SHIFT_PAYLOAD);
        await fetchGridData();
        emit('shift-allocated',props.day);
    } catch(error) {
        toast.add({severity:"error",summary: 'Allocate Shift failed',detail:"Internal Server Error", life:"4000"}); 
        console.log(`Grid for ${props.day},${props.location}:`,error);
    }
};

async function addName(name) {
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
    } catch(error) {
        if (error.response.status === 404) {
            toast.add({severity:"warn", summary:'Remove Name Failed', detail:"Name does not exist", life:"4000"});
            return;
        }
        toast.add({severity:"error", summary:'Remove Name Failed', detail:"Internal Server Eror", life:"4000"});
        console.log(`Grid for ${props.day}, ${props.location}:`, error);
    }
}

async function swapNames(names) {
    if (names.length !== 2) {
        console.log("swapNames method expecting input array of containing 2 strings");
        return;
    }
    const SWAP_NAMES_PAYLOAD = {
        "names" : names,
        "grid_name": GRID_NAME
    }
    try {
        const response = await axios.post(API_BASE_URL+endpoints.swapNames,SWAP_NAMES_PAYLOAD);
        await fetchGridData();
        toast.add({severity:'info', summary:'Swap Name', detail: `swapped ${names}`, life:"4000"});
    } catch(error) {
        toast.add({severity:"error", summary:'Swap Name Failed', detail:"Internal Server Eror", life:"4000"});
        console.log(`Grid for ${props.day}, ${props.location}:`, error);
    }
}

const allNames = computed(() => {
    let names = [];
    for (const row of rowData.value) {
        names.push(row[GRID_NAME]);
    }
    return names;
})

onMounted(async () => {
    await fetchGridData();
})
const rowData = ref([]);
const colDefs = ref([]);


defineExpose({ 
    addName, 
    removeName, 
    fetchGridData,
    swapNames,
    disableCellClicks,
    get allNames() {
        return allNames.value;
    }
});

</script>


<style>
/* Header cells */

/* Data cells */
.customGrid .ag-cell {
  transition: border 0.1s ease, box-shadow 0.2s ease;
}
/* On hover change border to blue */
.customGrid .ag-cell:hover {
  border: 1.5px solid #0768fa;
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

/* using domLayout:autoHeight this sets the min height when there are no rows */
.customGrid .ag-center-cols-viewport {
    min-height: 3vh !important;
}
</style>
