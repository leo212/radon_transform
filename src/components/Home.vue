<template>
    <div>
        <div class="md-title" v-if="files.length > 0">Uploaded Images</div>
        <md-empty-state
            v-if="files.length === 0"
            class="empty-state"
            md-icon="add_photo_alternate"
            md-label="No Images Loaded"
            md-description="Drag & drop an image file anywhere to load it"
        >
        </md-empty-state>
        <div class="imageList" v-else>
            <ImageCard
                v-for="file in files"
                v-on:action="transformImage(file)"
                :key="file.url"
                :filename="file.url"
                :name="file.name"
                action="Transform"
                :status="file.error ? 'error' : file.success ? 'success' : file.active ? 'pending' : ''"
            >
            </ImageCard>
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
                    <button ref="uploadButton" class="hidden" @click.prevent="$refs.upload.active = true">
                        Start Upload
                    </button>
                </div>
            </div>
        </div>
        <div class="md-title" v-if="resultFiles.length > 0">Transformed Images</div>
        <div class="resultList">
            <ImageCard
                v-for="file in resultFiles"
                v-on:action="reconstructImage(file)"
                :key="file.url"
                :filename="file.url"
                :name="file.name"
                action="Reconstruct"
                :status="file.error ? 'error' : file.success ? 'success' : file.active ? 'pending' : ''"
            >
            </ImageCard>
        </div>
        <md-snackbar :md-active.sync="showSnackbar" md-persistent :md-duration="Infinity">
            <span>{{ error }}</span>
            <md-button class="md-primary" @click="connectToServer()">Retry</md-button>
        </md-snackbar>
    </div>
</template>

<script>
import server from "../js/app.server";
let appGlobal = require("../js/app.global");
appGlobal.loadCss("static/css/home.css");

import Vue from "vue";
import ImageCard from "../components/ImageCard";

const VueUploadComponent = require("vue-upload-component");
Vue.component("file-upload", VueUploadComponent);

export default {
    data: function() {
        return {
            files: [],
            resultFiles: [],
            showSnackbar: false,
            error: ""
        };
    },
    created: function() {
        this.connectToServer();
    },
    components: {
        FileUpload: VueUploadComponent,
        ImageCard
    },
    methods: {
        transformImage: function(file) {
            this.$emit("transform", file);
        },
        reconstructImage: function(file) {
            this.$emit("reconstruct", file);
        },
        connectToServer: function() {
            let data = this.$data;
            data.showSnackbar = false;
            server
                .checkStatus(data)
                .then(() => {
                    data.files = [];
                    data.resultFiles = [];
                    server.getImageList(data.files);
                    server.getRadonList(data.resultFiles);
                })
                .catch(error => {
                    data.showSnackbar = true;
                    data.error = error;
                });
        }
    },
    watch: {
        // every time files to upload list changes
        files: function() {
            this.files.forEach(file => {
                if (file.success) file.url = server.getImageFileUrl(file.name);
            });
            // force click on the hidden upload button
            this.$refs.uploadButton.click();
        }
    }
};
</script>
