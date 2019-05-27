<template>
  <div class="transformLayout">
    <md-field>
      <label for="algorithm">Radon Algorithm</label>
      <md-select v-model="selectedAlgorithm" name="algorithm" id="algorithm">
        <md-option value="dss">Direct Slant Stack</md-option>
        <md-option value="pir">Parallel Image Rotation</md-option>
        <md-option value="shas">Shift and Sum</md-option>
        <md-option value="twoscale">Two-Scale Recursion</md-option>
        <md-option value="sss">Slow Slant Stack</md-option>
        <md-option value="fss">Fast Slant Stack</md-option>
      </md-select>
    </md-field>
    <div class="transformPics">
      <div class="sourceHolder">
        <img ref="sourceImage" class="source" :src="filename" :alt="name" />
      </div>
      <div v-if="progress > 0" class="targetHolder">
        <img
          class="target"
          :src="targetFilename + '?p=' + progress"
          :alt="name"
        />
      </div>
      <div
        v-else
        class="emptyImage"
        v-bind:style="{ width: imageWidth + 'px', height: imageHeight + 'px' }"
      ></div>
    </div>
    <b-progress
      class="progress"
      height="12px"
      :value="progress"
      :animated="animate"
      striped
    ></b-progress>
    <md-button class="md-raised md-primary" @click="runTransform()"
      >Transform</md-button
    >
    <md-button class="md-raised md-accent">Close</md-button>
  </div>
</template>

<script>
let appConfig = require("../js/app.config");
let requestId = 0;

export default {
  name: "Transform",
  data: () => {
    return {
      imageWidth: 0,
      imageHeight: 0,
      selectedAlgorithm: "dss",
      progress: 0,
      targetFilename: "",
      animate: false
    };
  },
  props: ["filename", "name"],
  mounted: function() {
    this.$data.imageWidth = this.$refs.sourceImage.width;
    this.$data.imageHeight = this.$refs.sourceImage.height;
  },

  methods: {
    runTransform() {
      let data = this.$data;

      // set target filename
      data.targetFilename =
        appConfig.PYTHON_SERVER_URL +
        appConfig.GET_IMAGE_RESULT_SERVICE +
        this.$props.name;

      data.animate = true;

      // run radon transform service on server
      fetch(
        appConfig.PYTHON_SERVER_URL +
          appConfig.TRANSFORM_SERVICE +
          this.$props.name
      ).then(response => {
        if (response.ok) {
          response.json().then(json => {
            requestId = json.requestId;
            // start an interval to check the job status until it will be completed
            let checkJobStatusFunc = function() {
              fetch(
                appConfig.PYTHON_SERVER_URL +
                  appConfig.GET_STATUS_SERVICE +
                  requestId
              ).then(response => {
                if (response.ok) {
                  response.json().then(json => {
                    data.progress = json.progress;
                    // if the process hasn't ended it, check it again within 500ms
                    if (data.progress < 100)
                      setTimeout(checkJobStatusFunc, 200);
                    else data.animate = false;
                  });
                }
              });
            };
            setTimeout(checkJobStatusFunc, 200);
          });
        }
      });
    }
  }
};
</script>

<style lang="scss" scoped>
.transformLayout {
  display: flex;
  flex-direction: column;
}

.transformPics {
  display: flex;
  align-items: center;
  flex-direction: row;
}
.sourceHolder {
  flex: 1;
  padding: 8px;
}

.targetHolder {
  flex: 1;
  padding: 8px;
}

.source {
  width: 100%;
  height: auto;
}

.emptyImage {
  background: black;
  flex: 1;
}

.target {
  width: 100%;
  height: auto;
}

.progress {
}
</style>
