import App from "@/App.vue";
import router from "@/router";
import "@/styles/globals.css";
import { OhVueIcon, addIcons } from "oh-vue-icons";
import { HiCheck, HiChevronDown, HiChevronUp, HiMinus, HiMoon, HiSun, SiGithub } from "oh-vue-icons/icons";
import { createPinia } from "pinia";
import { createApp } from "vue";

// icons
addIcons(HiChevronDown, HiChevronUp, HiCheck, HiMinus, HiSun, HiMoon, SiGithub);

const app = createApp(App);

app.component("v-icon", OhVueIcon);

app.use(createPinia());
app.use(router);

app.mount("#app");
