import Vue from "vue";
import Vuetify from "vuetify";
import App from "./App.vue";
import "vue-material/dist/vue-material.min.css";
import "vue-material/dist/theme/default.css";
import "vuetify/dist/vuetify.min.css";

import VueMaterial from "vue-material";

// Vue.use(BootstrapVue);
Vue.use(VueMaterial);
Vue.use(Vuetify);
Vue.config.productionTip = false;
// noinspection JSUnusedGlobalSymbols
new Vue({
    render: h => h(App)
}).$mount("#app");
