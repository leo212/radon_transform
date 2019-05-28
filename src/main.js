import Vue from "vue";
import App from "./App.vue";
// import "bootstrap/dist/css/bootstrap.css";
// import "bootstrap-vue/dist/bootstrap-vue.css";
import "vue-material/dist/vue-material.min.css";
import "vue-material/dist/theme/default.css";
import VueMaterial from "vue-material";
// import BootstrapVue from "bootstrap-vue";

// Vue.use(BootstrapVue);
Vue.use(VueMaterial);
Vue.config.productionTip = false;

// noinspection JSUnusedGlobalSymbols
new Vue({
  render: h => h(App)
}).$mount("#app");
