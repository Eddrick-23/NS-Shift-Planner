<template>
    <Drawer 
        v-model:visible="modelValue" 
        header="Sidebar" 
        :modal="false" 
        :dismissable="false"
        position="left" 
        class="!w-64 p-0 custom-drawer">
        <p>sidebar content</p>
    </Drawer>
</template> 

<script setup>
import Drawer from 'primevue/drawer';
const modelValue = defineModel();

</script>

<style>
/* Force the internal drawer panel width to be 16rem (256px) */
:deep(.p-drawer-left) {
  width: 16rem !important;
  max-width: 16rem !important;
}
</style>
