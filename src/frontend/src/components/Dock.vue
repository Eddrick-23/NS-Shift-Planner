
<template>
    <Dock :model="items">
        <template #itemicon="{ item }">
            <span v-tooltip.top="item.label" 
            class="flex items-center justify-center w-full h-full">
            <i :class="item.icon" class="dock-icon"
            @click = "onDockItemClick($event,item)"
            />
            </span>
        </template>
    </Dock>
    
    <Menu v-model="displayFinder"/>

</template>

<script setup>
import { ref } from "vue";
import Dock from 'primevue/dock';
import { useToast } from "primevue/usetoast";
import Menu from "./MenuCard.vue";
import axios from 'axios';

axios.defaults.withCredentials = true;
const toast = useToast();
const displayFinder = ref(false);

const compressLabel = ["Compress","Expand"];
const compressLogo = ["pi pi-arrow-down-left-and-arrow-up-right-to-center", "pi pi-arrow-up-right-and-arrow-down-left-from-center"]
let compressIdx = 0;
const compressAction = ref(compressLabel[compressIdx] + " Night Duty Grid");
const compressState = ref(compressLogo[compressIdx]);

const emit = defineEmits(['compress-night-duty-grid']);

const onDockItemClick = (event, item) => {
    if (item.command) {
        item.command();
    }

    event.preventDefault();
};

async function onCompressClick() {
    compressIdx ^= 1; //flip between 1 and 0
    compressState.value = compressLogo[compressIdx];
    compressAction.value = compressLabel[compressIdx] + " Night Duty Grid";
    emit('compress-night-duty-grid', compressIdx); //parent component handle callback
}

const items = ref([
  {
    label: 'Menu',
    icon: 'pi pi-bars',
    command:() => {
        displayFinder.value = true;
    }
  },
  {
    label: 'Version',
    icon: 'pi pi-thumbtack'
  },
  {
    label: 'Terms of Use & Privacy Policy',
    icon: 'pi pi-book'
  },
  {
    label: 'Keybinds',
    icon: 'pi pi-th-large'
  },
  {
    label: 'FAQ',
    icon: 'pi pi-question'
  },
  {
    label: compressAction,
    icon:compressState,
    command: async () =>{
        await onCompressClick();
    }
  }
]);

</script>

<style scoped>
.dock-icon {
    font-size: 2rem !important;
}
</style>
