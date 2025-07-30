<template>
    <Dialog 
    v-model:visible="model" 
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
                <template #header="{ chooseCallback, uploadCallback, clearCallback, files }">
                    <div class="flex items-center justify-center flex-1 gap-4">
                        <div class="flex gap-2">
                            <Button @click="chooseCallback()" icon="pi pi-images" rounded outlined severity="secondary"></Button>
                            <Button @click="uploadCallback" icon="pi pi-cloud-upload" rounded outlined severity="success" :disabled="!files || files.length === 0"></Button>
                            <Button @click="clearCallback()" icon="pi pi-times" rounded outlined severity="danger" :disabled="!files || files.length === 0"></Button>
                        </div>
                    </div>
                </template>
                <template #content>
                    <div class="flex flex-col items-center justify-center">
                        <p>Drag and drop files to here to upload.</p>
                        <p style="color:red">This action is irreversible!</p>
                    </div>
                </template>
            </FileUpload>
        </div>
        <Button label="Reset All (This action is irreversible!)" icon="pi pi-replay" severity="danger" class="w-full mt-2" @click="handleResetAll"/>
    </Dialog>
</template>

<script setup>
import Dialog from "primevue/dialog";
import FileUpload from 'primevue/fileupload';
import endpoints from "../api/api";
import { useToast } from "primevue/usetoast";
import axios from 'axios';

const toast = useToast();
const model = defineModel();
const API_BASE_URL = import.meta.env.VITE_BACKEND_DOMAIN;
const UPLOAD_ENDPOINT = API_BASE_URL + endpoints.upload;
const DOWNLOAD_ENDPOINT = API_BASE_URL + endpoints.download;
const RESET_ENDPOINT = API_BASE_URL + endpoints.resetAll; //DELETE Req

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
</script>
