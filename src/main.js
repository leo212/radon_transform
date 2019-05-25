import Vue from "vue";
import App from "./App.vue";
import "vue-material/dist/vue-material.min.css";
import "vue-material/dist/theme/default.css";
// noinspection ES6CheckImport
import VueMaterial from "vue-material";

Vue.use(VueMaterial);
Vue.config.productionTip = false;

// noinspection JSUnusedGlobalSymbols
new Vue({
  render: h => h(App)
}).$mount("#app");
