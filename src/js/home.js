import Vue from "vue";

const VueUploadComponent = require("vue-upload-component");
Vue.component("file-upload", VueUploadComponent);

let data = {
  serverStatus: "Checking...",
  files: []
};

export default {
  data: function() {
    return data;
  },
  components: {
    FileUpload: VueUploadComponent
  }
};

// check status of python server
fetch("http://localhost:8000/test")
  .then(response => {
    if (response.ok) {
      data.serverStatus = "OK";
    } else {
      data.serverStatus = "N/A";
    }
  })
  .catch(() => {
    data.serverStatus = "FAIL";
  });
