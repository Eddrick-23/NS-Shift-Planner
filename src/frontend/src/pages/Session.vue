<template>
  <div>
    <div v-if="loginFailed" class="w-full h-screen flex flex-col text-center justify-center">
      <p style="color: red">Login failed. Please try again later.</p>
    </div>
    
    <div v-else-if="!loading" class="p-4 flex">
      <LeftDrawer v-model="drawerVisible"/>
      <div class="relative min-h-screen transition-all duration-300 w-full" :class="{ 'ml-64': drawerVisible }">
        <div class="absolute bottom-4 left-0 -ml-4">
          <Button :icon="drawerVisible ? 'pi pi-arrow-left' : 'pi pi-arrow-right'" @click="drawerVisible = !drawerVisible"/>
        </div>
        <div class="grid grid-flow-col grid-cols-8 grid-rows-1 gap-2 ml-4 mr-4">
          <div class="col-span-2 flex flex-col items-center justify-center">
            <Select v-model="selectedGrid" :options="AllGrids" optionLabel="name" placeholder="Select Grid" optionValue="code" :showClear="true" class="w-full" />
          </div>
          <div class="col-span-2 flex flex-col items-center justify-center">
            <InputText type="text" placeholder="Name" v-model="typedName" class="w-full"/>
          </div>
          <div class="col-span-2 flex flex-col items-center justify-center">
            <ButtonGroup class="flex w-full">
              <Button icon="pi pi-plus" :disabled="!selectedGrid || !typedName" class="flex-1"/>
              <Button icon="pi pi-minus" :disabled="!selectedGrid || !typedName" class="flex-1"/>
            </ButtonGroup>
          </div>
          <div class="col-span-1 flex flex-col items-center justify-center">
            <LocationRadio v-model="selectedLocation"/> 
          </div>
          <div class="col-span-1 flex flex-col items-center justify-center"> 
            <ShiftSizeRadio v-model="selectedShiftSize"/>
          </div>
        </div>
        <Divider align="center" class="control-panel-divider">
          <b>Control Panel</b>
        </Divider> 
        <Grid :day="1" :location="'MCC'"/>
      </div>
    </div>
    <div v-else class="w-full h-screen flex flex-col text-center justify-center">
      <p>Loading...</p>
    </div>
  </div>
</template>


<script setup>
import Grid from '../components/Grid.vue';
import axios from 'axios';
import { onMounted,ref } from 'vue';
import endpoints from '../api/api';
import Divider from 'primevue/divider';
import Select from 'primevue/select';
import InputText from 'primevue/inputtext';
import ButtonGroup from 'primevue/buttongroup';
import Button from 'primevue/button';
import LocationRadio from '../components/LocationRadio.vue';
import ShiftSizeRadio from '../components/ShiftSizeRadio.vue';
import LeftDrawer from '../components/LeftDrawer.vue';
const apiBaseUrl = import.meta.env.VITE_BACKEND_DOMAIN

const loginFailed = ref(false);
const loading = ref(true);
const selectedLocation = ref('MCC'); //radio button
const selectedShiftSize = ref('Full'); // radio button
const selectedGrid = ref(null); // select UI
const AllGrids = ref([
  {name:'DAY1:MCC',code:'DAY1:MCC'},
  {name:'DAY1:HCC1',code:'DAY1:HCC1'},
  {name:'DAY1:HCC2',code:'DAY1:HCC2'},
  {name:'DAY2:MCC',code:'DAY2:MCC'},
  {name:'DAY2:HCC1',code:'DAY2:HCC1'},
  {name:'DAY2:HCC2',code:'DAY2:HCC2'},
  {name:'NIGHT DUTY', code:'DAY3:MCC'},
])
const typedName = ref(null); // input box
const drawerVisible = ref(true); 

onMounted(() => {
  axios.get(apiBaseUrl + endpoints.login, {
    withCredentials: true // send existing cookies if any
  })
  .then(response => {
    loading.value=false;
    console.log(response.data);
  })
  .catch(error => {
    loginFailed.value = true;
    loading.value = false;
    if (error.response) {
      console.log('Error response:', error.response.data);
      console.log('Status:', error.response.status);
    } else if (error.request) {
      console.log('No response received:', error.request);
    } else {
      console.log('Error:', error.message);
    }
  });
});

</script>


<style>
.control-panel-divider{
  --p-divider-border-color:#0a0100 
}
</style>
