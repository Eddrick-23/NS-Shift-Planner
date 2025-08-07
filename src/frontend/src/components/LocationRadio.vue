<template>
    <div class="flex flex-col gap-2">
        <div>
            <RadioButton v-model="modelValue" inputId="selectedLocation1" name="MCC" value="MCC" variant="filled"/>
            <label for="selectedLocation1">MCC</label>
        </div>
        <div>
            <RadioButton v-model="modelValue" inputId="selectedLocation2" name="HCC1" value="HCC1" variant="filled"/>
            <label for="selectedLocation2">HCC1</label>
        </div>
        <div>
            <RadioButton v-model="modelValue" inputId="selectedLocation3" name="HCC2" value="HCC2" variant="filled" />
            <label for="selectedLocation3">HCC2</label>
        </div>
    </div>
</template>


<script setup>
import RadioButton from 'primevue/radiobutton'
import { onBeforeUnmount, onMounted } from 'vue';

// enable v-model usage in parent
const modelValue = defineModel();

function handleKeyPress(event) {
    const el = document.activeElement;
    // el may be null so use ?. 
    // || false to force bool value
    const isTyping = el?.matches?.('input, textarea, [contenteditable]') || false;
    if (!isTyping) {
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
}

onMounted(() => {
    window.addEventListener('keydown',handleKeyPress);
})
onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleKeyPress);
})
</script>

