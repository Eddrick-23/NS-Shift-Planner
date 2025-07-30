<template>
    <Drawer 
        v-model:visible="modelValue" 
        header="Sidebar" 
        :modal="false" 
        :dismissable="false"
        position="left" 
        class="custom-drawer !w-100 p-0">
        <HourGrid ref="hourGrid" v-if="modelValue"/>
    </Drawer>
</template> 

<script setup>
import {ref} from 'vue';
import Drawer from 'primevue/drawer';
import HourGrid from '../components/HourGrid.vue';
const modelValue = defineModel();

const hourGrid = ref(null);

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
