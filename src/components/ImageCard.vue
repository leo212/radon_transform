<template>
  <md-card>
    <md-card-media-cover md-solid>
      <md-card-media md-ratio="1:1">
        <img :src="imageFilename" alt="Image" />
      </md-card-media>
      <md-card-area>
        <md-card-header>
          <span class="md-title">imagefile.png</span>
          <span class="md-subhead"></span>
        </md-card-header>

        <md-card-actions>
          <md-button class="md-icon-button">
            <md-icon md-label="Transform">blur_linear</md-icon>
          </md-button>
          <md-button class="md-icon-button">
            <md-icon md-label="Reconstruct">filter_b_and_w</md-icon>
          </md-button>
        </md-card-actions>
      </md-card-area>
    </md-card-media-cover>
  </md-card>
</template>

<script>
export default {
  name: "ImageCard"
};
</script>

<style scoped></style>
