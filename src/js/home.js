let appConfig = require("./app.config");
import Vue from "vue";
import ImageCard from "../components/ImageCard";

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
    FileUpload: VueUploadComponent,
    ImageCard
  },
  watch: {
    // every time files to upload list changes
    files: function() {
      this.files.forEach(file => {
        if (file.success)
          file.url =
            appConfig.PYTHON_SERVER_URL +
            appConfig.GET_IMAGE_SERVICE +
            file.name;
      });
      // force click on the hidden upload button
      this.$refs.uploadButton.click();
    }
  }
};

// check status of python server
fetch(appConfig.PYTHON_SERVER_URL + appConfig.SERVER_STATUS_SERVICE)
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

fetch(appConfig.PYTHON_SERVER_URL + appConfig.GET_IMAGE_LIST_SERVICE).then(
  response => {
    if (response.ok) {
      response.json().then(json => {
        json["file_list"].forEach(image => {
          data.files.push({
            url:
              appConfig.PYTHON_SERVER_URL + appConfig.GET_IMAGE_SERVICE + image,
            name: image,
            uploaded: true
          });
        });
      });
    }
  }
);
