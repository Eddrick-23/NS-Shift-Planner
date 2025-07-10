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
import Tab from 'primevue/tab';
import TabList from 'primevue/tablist';





const app = createApp(App);
app.use(router);
app.use(PrimeVue, {
    // Default theme configuration
    theme: {
        preset: Aura,
        options: {
            prefix: 'p',
            darkModeSelector: 'system',
            cssLayer: false
        }
    }
 });
 // Register components globally
app.component('Button', Button);
app.component('Tabs', Tabs);
app.component('TabPanel', TabPanel);
app.component('Tab', Tab);
app.component('TabList', TabList);
app.mount('#app');
