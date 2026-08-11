import { createApp } from 'vue'
import Chat from 'vue3-beautiful-chat'

import App from './App.vue'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'

import "./assets/main.css";
import "./assets/modal.css";
import "./assets/game.css";

import Toast, {POSITION} from "vue-toastification";
import "vue-toastification/dist/index.css";

createApp(App).use(Chat).use(Toast, {
    timeout: 5000,
    position: POSITION.TOP_CENTER
}).mount('#app')
