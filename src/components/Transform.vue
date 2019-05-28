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
      <div class="targetHolder">
        <div v-if="started" class="target">
          <img
            class="target"
            :src="targetFilename + '?p=' + progress"
            :alt="name"
          />
          <md-progress-bar
            md-mode="determinate"
            :md-value="progress"
          ></md-progress-bar>
        </div>
        <md-empty-state
          v-else
          class="beforeTransform"
          md-icon="assistant"
          md-label="Transform hasn't started yet"
          md-description="Choose an algorithm and click 'Transform' to start performing radon transform"
        />
      </div>
    </div>
    <md-button
      class="md-raised md-primary"
      :disabled="animate"
      @click="runTransform()"
      >Transform</md-button
    >
    <md-button class="md-raised md-accent" @click="closeTransform()"
      >Close</md-button
    >
    <md-snackbar :md-active.sync="showSnackbar" md-persistent>
      <span>{{ error }}</span>
      <md-button
        class="md-primary"
        @click="
          showSnackbar = false;
          runTransform();
        "
        >Retry</md-button
      >
    </md-snackbar>
    <div></div>
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
      started: false,
      targetFilename: "",
      animate: false,
      error: "",
      showSnackbar: false
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
      data.started = true;

      // run radon transform service on server
      fetch(
        appConfig.PYTHON_SERVER_URL +
          appConfig.TRANSFORM_SERVICE +
          this.$data.selectedAlgorithm +
          "/" +
          this.$props.name
      ).then(response => {
        if (response.ok) {
          response.json().then(json => {
            if (!json.error) {
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
            } else {
              data.started = false;
              data.animate = false;
              data.error = "Server Error: " + json.error;
              data.showSnackbar = true;
            }
          });
        }
      });
    },
    closeTransform() {
      this.$emit("closeTab", this.$props.name);
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
  display: flex;
  justify-content: center;
  flex: 1;
  padding: 8px;
}

.targetHolder {
  display: flex;
  justify-content: center;
  flex: 1;
  padding: 8px;
}

.source {
  max-width: 512px;
  width: 100%;
  height: 100%;
}

.emptyImage {
  background: black;
  flex: 1;
}

.target {
  max-width: 512px;
  width: 100%;
  height: 100%;
}

.beforeTransform {
  transition: none;
}

.progress {
}
</style>
