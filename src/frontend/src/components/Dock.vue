
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
    <div class="flex flex-col items-center justify-center gap-2">
      <p> This app is currently in beta and may be unstable. </p>
      <p style="color: red;"> Sessions not modified for {{24 * DATA_STORED_DURATION}} hours are deleted</p>
      <p> You may save your work as a zip file by clicking on the menu in the dock</p>
      <p> Refer to detailed 
        <a href="https://github.com/Eddrick-23/NS-Shift-Planner/blob/main/CHANGELOG.md" style="color: blue;" class="underline">
          CHANGELOGS
        </a> 
      </p>
    </div>
    </Dialog>
    <Dialog v-model:visible="displayTermsAndPrivacyCard"
    :modal="true"
    header='Terms of Service and Privacy Policy'
    :style="{width : '40vw'}"
    :dismissable-mask="true"
    >
    <div class="flex flex-col items-center justify-center gap-2">
      <p> By using this app you agree to the Terms of Service and Privacy Policy </p>
      <p> Read the 
        <a href="https://github.com/Eddrick-23/NS-Shift-Planner/blob/main/CHANGELOG.md" style="color: blue;" class="underline">
          Terms of Service 
        </a> 
      </p>
      <p> Read the
        <a href="https://github.com/Eddrick-23/NS-Shift-Planner/blob/main/CHANGELOG.md" style="color: blue;" class="underline">
          Privacy Policy 
        </a> 
      </p>
    </div>
    </Dialog>
    <Dialog v-model:visible="displayKeybindsCard"
    :modal="true"
    header="Keybinds"
    :style="{width : '40vw'}"
    :dismissable-mask="true"
    >
    <div class="flex flex-col items-center justify-center gap-2">
      <p> Here are useful keybinds to toggle radio buttons</p>
      <p> <strong>Active location</strong></p>
      <div>
        <li>MCC -> "1" key</li>
        <li>HCC1 -> "2" key</li>
        <li>HCC2 -> "3" key</li>
      </div>
      <p> <strong>Allocation size</strong></p>
      <div>
        <li>first 30min -> "a" key</li>
        <li>full -> "s" key</li>
        <li>last 30min -> "d" key</li>
      </div>
    </div>
    </Dialog>
    <Dialog
      v-model:visible="displayFAQCard"
      :modal="true"
      header="Frequently Asked Questions"
      :style="{ width: '40vw' }"
      :dismissable-mask="true"
    >
      <div class="flex flex-col gap-4 px-4 py-2">
        <div
          v-for="(faq, index) in faqList"
          :key="index"
          class="border-b border-gray-300 pb-3"
        >
          <p class="font-semibold text-lg text-gray-800">{{ faq.question }}</p>
          <p class="text-sm text-gray-600 mt-1">{{ faq.answer }}</p>
        </div>
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
const displayTermsAndPrivacyCard = ref(false);
const displayKeybindsCard = ref(false);
const displayFAQCard = ref(false);

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
      displayVersionCard.value = true;
    }
  },
  {
    label: 'Terms of Service & Privacy Policy',
    icon: 'pi pi-book',
    command:() => {
      displayTermsAndPrivacyCard.value = true;
    }
  },
  {
    label: 'Keybinds',
    icon: 'pi pi-th-large',
    command: () => {
      displayKeybindsCard.value = true;
    }
  },
  {
    label: 'FAQ',
    icon: 'pi pi-question',
    command: () => {
      displayFAQCard.value = true;
    }
  },
  {
    label: compressAction,
    icon:compressState,
    command: async () =>{
        await onCompressClick();
    }
  }
]);

const faqList = [
  {
    question: "How do I allocate a shift",
    answer: "After adding a name, simply click on the cell directly. Use the radio buttons to adjust location and allocation size"
  },
  {
    question: "Is my work automatically saved",
    answer: `Sessions are saved in a cloud database, sessions not modified for ${24 * DATA_STORED_DURATION} hours are removed. If you may need to continue your work a few days later, you are advised to save your work as a zip file.`
  },
  {
    question: "How do I manually save my work?",
    answer: "Click on the Menu on the dock. You can then download your work as a zip file. You can reupload this zip file to resume."
  },
  {
    question: "Where is the HCC2 grid?",
    answer: "HCC2 grids are automatically hidden by default when empty, adding a name will make it appear."
  },
  {
    question: "Is there a way to reset/Clear All?",
    answer: "Click on the menu on the dock, there will be a reset all button. Note that this action is irreversible."
  },
];


</script>

<style scoped>
.dock-icon {
  font-size: 2rem !important;
  transition: transform 0.3s ease;
}

.dock-icon:hover {
  transform: scale(1.25);
}
</style>
