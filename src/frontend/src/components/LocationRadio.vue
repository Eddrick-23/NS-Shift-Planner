<template>
    <div class="flex flex-col gap-2">
        <div>
            <RadioButton v-model="modelValue" inputId="selectedLocation1" name="MCC" value="MCC" variant="filled"/>
            <label for="ingredient1">MCC</label>
        </div>
        <div>
            <RadioButton v-model="modelValue" inputId="selectedLocation2" name="HCC1" value="HCC1" variant="filled"/>
            <label for="ingredient2">HCC1</label>
        </div>
        <div>
            <RadioButton v-model="modelValue" inputId="selectedLocation3" name="HCC2" value="HCC2" variant="filled" />
            <label for="ingredient3">HCC2</label>
        </div>
    </div>
</template>


<script setup>
import RadioButton from 'primevue/radiobutton'
import { onBeforeUnmount, onMounted } from 'vue';

// enable v-model usage in parent
const modelValue = defineModel();

function handleKeyPress(event) {
    if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA' ) {
        if (['1','2','3'].includes(event.key)){
            event.preventDefault();
        }
    }
    switch(event.key) {
        case '1':
            modelValue.value = 'MCC';
            break;
        case '2':
            modelValue.value = 'HCC1';
            break;
        case '3':
            modelValue.value = 'HCC2';
            break;
    }
}

onMounted(() => {
    window.addEventListener('keydown',handleKeyPress);
})
onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleKeyPress);
})
</script>

