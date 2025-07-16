<template>
  <div>
    <div v-if="loginFailed" class="w-full h-screen flex flex-col text-center justify-center">
      <p style="color: red">Login failed. Please try again later.</p>
    </div>
    <div v-else-if="!loading">
      <p>Session Page</p>
      <Grid :day="1" :location="'MCC'"/>
    </div>
    <div v-else class="w-full h-screen flex flex-col text-center justify-center">
      <p>Loading...</p>
    </div>
  </div>
</template>


<script setup>
import Grid from '../components/Grid.vue'
import axios from 'axios'
import { onMounted,ref } from 'vue'
import endpoints from '../api/api'

const apiBaseUrl = import.meta.env.VITE_BACKEND_DOMAIN

const loginFailed = ref(false);
const loading = ref(true);

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
