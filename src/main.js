import Vue from "vue";
import App from "./App.vue";
import "vue-material/dist/vue-material.min.css";
import "vue-material/dist/theme/default.css";
// noinspection ES6CheckImport
import {
  MdButton,
  MdCard,
  MdContent,
  MdEmptyState,
  MdField,
  MdIcon,
  MdList,
  MdRipple,
  MdTabs
} from "vue-material/dist/components";

// Vue.use(MdFile);
// Vue.use(MdInput);
Vue.use(MdButton);
Vue.use(MdField);
Vue.use(MdField);
Vue.use(MdContent);
Vue.use(MdTabs);
Vue.use(MdIcon);
Vue.use(MdCard);
Vue.use(MdRipple);
Vue.use(MdEmptyState);
Vue.use(MdList);
Vue.config.productionTip = false;

// noinspection JSUnusedGlobalSymbols
new Vue({
  render: h => h(App)
}).$mount("#app");
