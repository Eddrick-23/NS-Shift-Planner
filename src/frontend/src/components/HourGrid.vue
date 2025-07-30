<template>
    <div v-if="!fetchDataSuccessful" class="w-full flex flex-col text-center justify-center">
        <p style="color: red">Unable to fetch grid data</p>
    </div>
    <div v-else class="w-full">
        <ag-grid-vue
            dom-layout="autoHeight"
            :row-height="30"
            :header-height="30"
            :theme="myTheme"
            :rowData="rowData"
            :columnDefs="colDefs"
            :pinned-bottom-row-data="pinnedBottomRowData"
        />
    </div>
</template>

<script setup>
import { onMounted, ref} from 'vue';
import { AgGridVue } from 'ag-grid-vue3';
import {themeQuartz, colorSchemeLightCold} from 'ag-grid-community'; 
import axios from 'axios';
import endpoints from "../api/api.js";

const myTheme = themeQuartz.withParams({
    headerColumnBorder:{style:'solid',width:"1px"},
    headerRowBorder: {style:'solid',width:"1px"},
    rowBorder: { style: 'solid',width:"1.5px"},
    columnBorder: { style: 'solid',width:"1.5px"}, 
    fontSize:12,
    headerFontSize:10
}).withPart(colorSchemeLightCold);

axios.defaults.withCredentials = true;
const API_BASE_URL = import.meta.env.VITE_BACKEND_DOMAIN;

const fetchDataSuccessful = ref(true);
async function fetchHourData() {
    try {
        const response = await axios.get(API_BASE_URL+endpoints.hours);
        const newColDefs = response.data.columnDefs;
        const newRowData = response.data.rowData;
        const newPinnedBottomRowData = response.data.pinnedBottomRowData;
        updateGrid(newColDefs,newRowData,newPinnedBottomRowData);
        fetchDataSuccessful.value=true;
    }catch(error) {
        fetchDataSuccessful.value=false;
        console.log('Hour Grid:',error);
    }
}

function updateGrid(newColDefs,newRowData, newPinnedBottomRowData) {
    addStyle(newColDefs);
    colDefs.value = newColDefs;
    rowData.value = newRowData;
    pinnedBottomRowData.value = newPinnedBottomRowData;
}

function addStyle(colDefs) {
    colDefs.forEach(colDef => {
        if (colDef.field === "Name") {
            colDef.width = 100;
            colDef.suppressSizeToFit = true;
        }else {
            colDef.flex = 1;
            colDef.resizable = false;
        }
    })
}

const rowData = ref([]);
const colDefs = ref([]);
const pinnedBottomRowData = ref([]);

onMounted(async () => {
    await fetchHourData();
})

defineExpose({fetchHourData});
</script>
