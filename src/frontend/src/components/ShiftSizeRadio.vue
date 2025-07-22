<template>
    <div class="flex flex-col gap-2">
        <div>
            <RadioButton v-model="modelValue" inputId="selectedSize1" name="first 30min" value="0.25" variant="filled"/>
            <label for="ingredient1">First 30min</label>
        </div>
        <div>
            <RadioButton v-model="modelValue" inputId="selectedSize2" name="full" value="1" variant="filled"/>
            <label for="ingredient2">Full</label>
        </div>
        <div>
            <RadioButton v-model="modelValue" inputId="selectedSize3" name="last 30min" value="0.75" variant="filled" />
            <label for="ingredient3">Last 30min</label>
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
    const isTyping = el?.matches?.('input, textarea, [contenteditable]') || false; //makesure always bool
    if (!isTyping) {
       switch(event.key) {
            case 'a':
                modelValue.value = '0.25';
                break;
            case 's':
                modelValue.value = '1';
                break;
            case 'd':
                modelValue.value = '0.75';
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

