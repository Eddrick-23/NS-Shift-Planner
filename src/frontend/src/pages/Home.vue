<template>
  <div class="h-screen flex flex-col gap-4">
    <section class="flex-shrink-0">
      <div class="relative flex items-center justify-center h-20 overflow-hidden">
        <!--Background-->
        <GridShuffle class="absolute inset-0 z-0 pointer-events-none" />
        <!-- Foreground text -->
        <p class="relative z-10 text-4xl font-bold">NS Shift Planner</p>
      </div>
    </section>
    
    <!-- Main content grid that takes remaining space -->
    <div class="flex-1 grid grid-cols-2 gap-4 min-h-0">
      <!-- Left half: full height -->
      <div class="ml-4 mr-4">
        <LandingTabs />
      </div>
      
      <!-- Right half: split into two rows -->
      <section class="grid grid-rows-1 gap-4 overflow-hidden">
        <div class="mb-4">
          <Card class="new-session-card border border-transparent h-full flex items-center justify-center mr-4 duration-300 hover:border-gray-600">
            <template #title>
              <p class="p-2 text-center">Sessions unused for 24 hours or more are deleted.</p>
              <p class="p-2 text-center text-sm">download as a ZIP file if needed</p>
            </template>
            <template #content>
              <Button label="Start Planning" icon="pi pi-sparkles" class="w-full" v-on:click="goToSession"/>
            </template>
          </Card>
        </div> 
      </section>
    </div>
  </div>
</template>

<style scoped>
html, body{
  height:100%;
  margin:0;
  overflow:hidden; /* Prevent scrolling */
}
.new-session-card {
  --p-card-border-radius: 12px;
  --p-card-border: 1px solid #d1d5db;
}
.resume-session-card {
  --p-card-border-radius: 12px;
  --p-card-border: 1px solid #d1d5db;
}
</style>

<script setup>
import GridShuffle  from '../components/GridShuffle.vue'; 
import Card from 'primevue/card';
import LandingTabs from '../components/LandingTabs.vue';
import {useRouter} from 'vue-router'
const router =useRouter(); 

function goToSession() {
  router.push('/session');
}
</script>
