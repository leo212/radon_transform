import Vue from "vue";
import ImageCard from "../components/ImageCard";

const VueUploadComponent = require("vue-upload-component");
Vue.component("file-upload", VueUploadComponent);

let data = {
  serverStatus: "Checking...",
  files: [],
  uploadedFiles: []
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
      // force click on the hidden upload button
      this.$refs.uploadButton.click();
    }
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

fetch("http://localhost:8000/get_filelist").then(response => {
  if (response.ok) {
    response.json().then(json => {
      data.uploadedFiles = json.file_list;
    });
  }
});
