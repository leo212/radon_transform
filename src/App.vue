<template>
  <div>
    <md-tabs class="md-primary" md-alignment="fixed">
      <md-tab id="tab-home" md-label="Home" md-icon="home"><Home /></md-tab>
      <md-tab id="tab-pages" md-label="Transform" md-icon="transform">
        TBD
      </md-tab>
      <md-tab id="tab-favorites" md-label="Reconstruct" md-icon="restore_page">
        TBD
      </md-tab>
    </md-tabs>
  </div>
</template>

<script>
import Home from "./components/Home";

export default {
  components: {
    Home
  }
};
</script>
