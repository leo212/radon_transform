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
      md-description="Drag & drop an image file anywhere to load it"
    >
    </md-empty-state>
    <div class="imageList" v-else>
      <ImageCard
        v-for="file in files"
        :key="file.url"
        :filename="file.url"
        :name="file.name"
        :status="
          file.error
            ? 'error'
            : file.success
            ? 'success'
            : file.active
            ? 'pending'
            : ''
        "
      ></ImageCard>
    </div>
    <div class="drag-area">
      <div v-show="$refs.upload && $refs.upload.dropActive" class="drop-active">
        <span id="dropFilesText" class="md-title">Drop files to upload</span>
      </div>
      <div class="upload">
        <div>
          <MdButton class="md-primary md-raised">
            <!--suppress XmlInvalidId -->
            <label for="file">
              Upload an image file
            </label>
          </MdButton>
        </div>
        <div>
          <file-upload
            post-action="http://localhost:8000/upload/"
            :multiple="true"
            extensions="gif,jpg,jpeg,png,webp"
            accept="image/png,image/gif,image/jpeg,image/webp"
            :drop="true"
            :drop-directory="true"
            v-model="files"
            ref="upload"
          >
          </file-upload>
          <button
            ref="uploadButton"
            class="hidden"
            @click.prevent="$refs.upload.active = true"
          >
            Start Upload
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script src="../js/home.js"></script>
<style lang="scss" scoped>
@import "../css/home.css";
</style>
