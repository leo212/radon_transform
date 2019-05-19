<template>
  <div>
    <div>
      Python Server Status:
      <span v-if="serverStatus === 'OK'" class="status -success"></span>
      <span v-else-if="serverStatus === 'FAIL'" class="status -failure"></span>
      <span v-else class="status -pending"></span>
      {{ serverStatus }}
    </div>
    <md-empty-state
      v-if="files.length === 0"
      md-icon="add_photo_alternate"
      md-label="No Images Loaded"
      md-description="Drag & drop an image file anywhere to load it">
    </md-empty-state>
    <div class="drag-area">
      <div v-show="$refs.upload && $refs.upload.dropActive" class="drop-active">
        <span id="dropFilesText" class="md-title">Drop files to upload</span>
      </div>
      <div class="upload">
        <md-list v-if="files.length">
          <md-list-item v-for="(file, index) in files" :key="file.id">
            <md-icon>image</md-icon>
            <span class="md-list-item-text">{{ file.name }} ({{ file.size }} bytes)</span>
            <div v-if="file.error" class="status -failure"></div>
            <div v-else-if="file.success" class="status -success"></div>
            <div v-else-if="file.active" class="status -pending"></div>
            <span v-else></span>
          </md-list-item>
        </md-list>
        <div>
          <label
            for="file" class="button md-button md-primary md-raised md-theme-default">
            <div class="md-ripple">
              <div class="md-button-content">Choose an image file</div>
            </div>
          </label>
        </div>
        <div>
          <file-upload
            post-action="http://localhost:8000/upload/"
            :multiple="true"
            :drop="true"
            :drop-directory="true"
            v-model="files"
            ref="upload">
          </file-upload>
          <MdButton class="md-primary md-raised"
            v-if="files.length && (!$refs.upload || !$refs.upload.active)"
            @click.prevent="$refs.upload.active = true">
            Start Upload
          </MdButton>
          <MdButton
            class="md-primary md-raised"
            v-else-if="($refs.upload && $refs.upload.active)"
            @click.prevent="$refs.upload.active = false">
            Stop Upload
          </MdButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script src="../js/home.js"></script>

<style lang="scss" scoped>
@import "../css/home.css";
</style>
