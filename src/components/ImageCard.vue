<template>
  <md-card class="md-card">
    <md-card-media>
      <md-ripple>
        <img v-if="filename" :src="filename" :alt="name" />
      </md-ripple>
    </md-card-media>

    <md-card-header class="md-card-header">
      <span class="md-title">{{ name }}</span>
      <span class="md-subhead"></span>
    </md-card-header>

    <md-card-actions md-alignment="space-between" class="md-card-actions">
      <div :class="[statusClass, status]"></div>
      <md-button class="md-primary" @click="onTransformClick()"
        >Transform</md-button
      >
    </md-card-actions>
  </md-card>
</template>

<script>
export default {
  name: "ImageCard",
  data: () => {
    return {
      statusClass: "status"
    };
  },
  props: ["filename", "name", "status"],
  methods: {
    onTransformClick: function() {
      this.$emit("transformImage");
    }
  }
};
</script>

// noinspection CSSUnusedGlobalSymbols
<style scoped>
.md-card {
  width: 160px;
  margin: 4px;
  display: inline-block;
  vertical-align: top;
}

.md-card .md-title {
  font-size: 12px;
  line-height: 8px;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
  display: block;
  padding-top: 4px;
  padding-bottom: 4px;
}

.md-card-media + .md-card-header {
  padding-top: 4px;
}

.md-card-actions {
  padding: 0;
}

.md-card-header {
  padding: 8px;
}
</style>
