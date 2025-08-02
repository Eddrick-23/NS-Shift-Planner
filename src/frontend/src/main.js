import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import {router} from './router'
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura';
import 'primeicons/primeicons.css'
import Button from 'primevue/button'
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
import Toast from 'primevue/toast';
import ToastService from 'primevue/toastservice';
import Tooltip from 'primevue/tooltip'

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
app.directive('tooltip', Tooltip);
 // Register components globally
app.component('Toast',Toast);
app.component('Button', Button);
app.mount('#app');
