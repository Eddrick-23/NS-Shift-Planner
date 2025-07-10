<template>
  <div class="h-screen flex flex-col gap-4">
    <!-- Top section with fixed height -->
    <section class="flex-shrink-0">
      <div class="relative flex items-center justify-center h-20 overflow-hidden">
        <!-- Grid background fills the container -->
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
      <section class="grid grid-rows-2 gap-4 overflow-hidden">
        <div>
          <Card class="new-session-card border border-transparent h-full flex items-center justify-center mr-4 duration-300 hover:border-gray-600">
            <template #title>
              <p class="p-2 text-center">New session</p>
            </template>
            <template #content>
              <p class="p-2">Start a fresh session with a new session ID</p>
              <Button label="Create New Session" icon="pi pi-sparkles" class="w-full"/>
            </template>
          </Card>
        </div>
        <div>
          <Card class="resume-session-card border border-transparent h-full flex items-center justify-center mr-4 duration-300 hover:border-gray-600">
            <template #title>
              <p class="p-2 text-center">Resume Session</p>
            </template>
            <template #content>
              <p class="p-2">Resume a session using an existing session ID</p>
              <Button label="Resume Existing Session" icon="pi pi-play" class="w-full"/>
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

<script>
import GridShuffle  from '../components/GridShuffle.vue'; 
import Card from 'primevue/card';
import LandingTabs from '../components/LandingTabs.vue';

export default {
  components: {
    GridShuffle,
    Card,
    LandingTabs,
  },
};
</script>
