import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import {router} from './router'
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura';
import 'primeicons/primeicons.css'
import Button from 'primevue/button'
import Tabs from 'primevue/tabs';
import TabPanel from 'primevue/tabpanel';
import TabPanels from 'primevue/tabpanels'
import Tab from 'primevue/tab';
import TabList from 'primevue/tablist';
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
import Toast from 'primevue/toast';
import ToastService from 'primevue/toastservice';

// Register all Community features
ModuleRegistry.registerModules([AllCommunityModule]);



const app = createApp(App);
app.use(router);
app.use(PrimeVue, {
    // Default theme configuration
    theme: {
        preset: Aura,
        options: {
            prefix: 'p',
            darkModeSelector: 'light',
            cssLayer: false
        }
    }
 });
app.use(ToastService);
 // Register components globally
app.component('Toast',Toast);
app.component('Button', Button);
app.component('Tabs', Tabs);
app.component('TabPanel', TabPanel);
app.component('TabPanels', TabPanels);
app.component('Tab', Tab);
app.component('TabList', TabList);
app.mount('#app');
