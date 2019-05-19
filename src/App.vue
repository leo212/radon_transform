<template>
  <div>
    <md-tabs class="md-primary" md-alignment="left">
      <md-tab id="tab-home" md-label="Home" md-icon="home"><Home /></md-tab>
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
