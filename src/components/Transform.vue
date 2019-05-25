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
      <md-button class="md-icon-button md-raised md-primary">
        <md-icon>navigate_next</md-icon>
      </md-button>
      <div v-if="result !== ''" class="targetHolder">
        <img class="target" :src="result" :alt="resultName" />
      </div>
      <div
        v-else
        class="emptyImage"
        v-bind:style="{ width: imageWidth + 'px', height: imageHeight + 'px' }"
      ></div>
    </div>
    <md-progress-bar
      md-mode="determinate"
      :md-value="progress"
    ></md-progress-bar>
    <md-button class="md-raised md-accent">Close</md-button>
  </div>
</template>

<script>
export default {
  name: "Transform",
  data: () => {
    return {
      result: "",
      resultName: "",
      imageWidth: 0,
      imageHeight: 0,
      selectedAlgorithm: "dss",
      progress: 0
    };
  },
  props: ["filename", "name"],
  mounted: function() {
    this.$data.imageWidth = this.$refs.sourceImage.width;
    this.$data.imageHeight = this.$refs.sourceImage.height;
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
}

.targetHolder {
  flex: 1;
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
</style>
