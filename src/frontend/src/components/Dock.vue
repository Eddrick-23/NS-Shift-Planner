
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
    <Dialog 
    v-model:visible="displayFinder" 
    header="Menu" 
    :modal="true"
    :style="{ width: '40vw' }" 
    :dismissable-mask="true"
    >
        <Button label="Source code" severity="contrast" icon="pi pi-github" class="w-full mb-2" @click="redirectToSourceCode"/>
        <Button label="Save as Zip" icon="pi pi-download" class="w-full mb-2" @click="onFileDownload"/>
        <div class="card border border-gray-500">
            <FileUpload 
            name="file" 
            :url="UPLOAD_ENDPOINT"
            accept=".zip" 
            @upload="onFileUpload"
            @error="onFileUploadError"
            :multiple="false" 
            :maxFileSize="1000000"
            :with-credentials="true"
            >
                <template #empty>
                    <span>Drag and drop files to here to upload.</span>
                </template>
            </FileUpload>
        </div>
        <Button label="Reset All (This action is irreversible!)" icon="pi pi-replay" severity="danger" class="w-full mt-2" @click="handleResetAll"/>
    </Dialog>

</template>

<script setup>
import { ref } from "vue";
import Dialog from "primevue/dialog";
import FileUpload from 'primevue/fileupload';
import Dock from 'primevue/dock';
import endpoints from "../api/api";
import { useToast } from "primevue/usetoast";
import axios from 'axios';

axios.defaults.withCredentials = true;
const toast = useToast();
const displayFinder = ref(false);
const API_BASE_URL = import.meta.env.VITE_BACKEND_DOMAIN;
const UPLOAD_ENDPOINT = API_BASE_URL + endpoints.upload;
const DOWNLOAD_ENDPOINT = API_BASE_URL + endpoints.download;
const RESET_ENDPOINT = API_BASE_URL + endpoints.resetAll; //DELETE Req


const onDockItemClick = (event, item) => {
    if (item.command) {
        item.command();
    }

    event.preventDefault();
};


const redirectToSourceCode = (() => {
    window.open(import.meta.env.VITE_SOURCE_CODE_URL,"_blank");    
})

async function onFileDownload() {
    try {
        const response = await axios.post(DOWNLOAD_ENDPOINT, null, {
        responseType: 'blob',
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'planning.zip');
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
    } catch (error) {
      toast.add({severity:'error', summary:'Download Failed', detail:'File download failed due to Internal Server Error', life: 5000});
    }
}

function onFileUploadError(event) {
      toast.add({severity:'error', summary:'Upload Failed', detail:'File upload failed. File may be incompatible/corrupted', life: 5000});
}

function onFileUpload(event) {
    //reload entire page
    window.location.reload();
}

async function handleResetAll() {
    try {
        const response = await axios.delete(RESET_ENDPOINT);
        window.location.reload();
    } catch(error) {
        toast.add({severity:'error', summary:'Reset Failed', detail:'Reset failed due to internal server error', life: 5000});
    }
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
  }
]);

</script>

<style scoped>
.dock-icon {
    font-size: 2rem !important;
}
</style>
