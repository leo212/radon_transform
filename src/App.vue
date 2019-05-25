<template>
  <div>
    <md-tabs class="md-primary" md-alignment="left" :md-active-tab="activeTab">
      <md-tab id="tab-home" md-label="Home" md-icon="home"
        ><Home v-on:transform="transform"
      /></md-tab>
      <md-tab
        v-for="image in images"
        :md-label="image.name"
        :key="image.url"
        :id="image.url"
        md-icon="image"
      >
        <Transform :filename="image.url" :name="image.name"></Transform>
      </md-tab>
    </md-tabs>
  </div>
</template>

<script>
import Home from "./components/Home";
import Transform from "./components/Transform";

let openedTabs = {};
let images = [];

export default {
  data: () => {
    return {
      images: images,
      activeTab: "tab-home"
    };
  },
  methods: {
    transform(file) {
      if (!openedTabs[file.url]) {
        openedTabs[file.url] = true;
        images.push(file);
      }
      this.$data["activeTab"] = file.url;
    }
  },
  components: {
    Transform,
    Home
  }
};
</script>
