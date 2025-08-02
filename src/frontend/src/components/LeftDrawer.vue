<template>
    <Drawer 
        v-model:visible="modelValue" 
        header="Sidebar" 
        :modal="false" 
        :dismissable="false"
        position="left" 
        class="custom-drawer !w-110 p-0">
        <HourGrid ref="hourGrid" v-if="modelValue"/>
        <Divider />
        <p class="flex items-center justify-center mb-2">Swap names</p>
        <Select
        v-model="selectedGrid"
        :options="ALL_GRIDS" 
        optionLabel="name" 
        placeholder="Select Grid" 
        optionValue="code" 
        :showClear="true" 
        class="w-full mb-2" />
        <MultiSelect
        v-model="selectedNames"
        placeholder="Select 2 Names"
        :selection-limit="2"
        :options="getGridNames"
        :disabled="!selectedGrid"
        :show-clear="true"
        class="w-full mb-2"
        />
        <div class="flex w-full">
          <Button 
          @click="onSwapClick"
          icon="pi pi-arrow-right-arrow-left" 
          class="flex-1"
          :disabled="!(selectedGrid && selectedNames?.length >= 2 && selectedNames.every(name => name !== null))"
          />
        </div>
    </Drawer>
</template> 

<script setup>
import {ref, computed, watch} from 'vue';
import Drawer from 'primevue/drawer';
import Divider from 'primevue/divider';
import Select from 'primevue/select';
import MultiSelect from 'primevue/multiselect';
import HourGrid from '../components/HourGrid.vue';
const modelValue = defineModel();

const props = defineProps({
  gridMap :{
    type:Object,
    required:true
  }
});

const hourGrid = ref(null);
const selectedGrid = ref(null);
const selectedNames = ref(null);

const testNames = ["test1","test2","test3"];
const ALL_GRIDS = ref([
  {name:'DAY1:MCC',code:'DAY1:MCC'},
  {name:'DAY1:HCC1',code:'DAY1:HCC1'},
  {name:'DAY1:HCC2',code:'DAY1:HCC2'},
  {name:'DAY2:MCC',code:'DAY2:MCC'},
  {name:'DAY2:HCC1',code:'DAY2:HCC1'},
  {name:'DAY2:HCC2',code:'DAY2:HCC2'},
  {name:'NIGHT DUTY', code:'DAY3:MCC'},
]);

async function onSwapClick() {
  // call swapNames on target grid
  // refresh hour grid data
  console.log("swap click");
  const targetGrid = selectedGrid.value;
  const grid = props.gridMap.get(targetGrid);

  await grid?.value?.swapNames(selectedNames.value);
  await hourGrid?.value?.fetchHourData();
}

const getGridNames = computed(() => {
  //get the selected target grid
  // call the allNames function to get all available names
  const targetGrid = selectedGrid.value;
  const grid = props.gridMap.get(targetGrid);

  return grid?.value?.allNames;
});

//listener to update selectedNames in case a selected name is removed
watch(getGridNames, (newOptions) => {
  selectedNames.value = (selectedNames.value || []).filter(name =>
    newOptions.includes(name)
  );
});


//expose to parent
defineExpose({
  hourGrid,
});
</script>

<style>
/* Force the internal drawer panel width to be 16rem (256px) */
:deep(.p-drawer-left) {
  width: 16rem !important;
  max-width: 16rem !important;
}
.custom-drawer {
  --p-drawer-background : #f5f5f5;
}
</style>
