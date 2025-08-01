
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
    
    <Menu v-model="displayMenu"/>

    <Dialog v-model:visible="displayVersionCard"
    :modal="true"
    :header="VERSION_HEADER"
    :style="{width : '40vw'}"
    :dismissable-mask="true"
    >
    <div class="flex flex-col items-center justify-center">
      <p> This app is currently in beta and may be unstable. </p>
      <p style="color: red;"> Sessions not modified for {{24 * DATA_STORED_DURATION}} hours are deleted</p>
    </div>
    </Dialog>

</template>

<script setup>
import { ref } from "vue";
import Dock from 'primevue/dock';
import { useToast } from "primevue/usetoast";
import Menu from "./MenuCard.vue";
import Dialog from "primevue/dialog";
import axios from 'axios';

axios.defaults.withCredentials = true;
const toast = useToast();
const displayMenu = ref(false);
const displayVersionCard = ref(false);

const VERSION_HEADER = `Version ${import.meta.env.VITE_VERSION}`;
const DATA_STORED_DURATION = import.meta.env.VITE_DATA_SAVED_DURATION;
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
        displayMenu.value = true;
    }
  },
  {
    label: 'Version',
    icon: 'pi pi-thumbtack',
    command:() => {
      console.log("clicked version");
      displayVersionCard.value = true;
    }
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
