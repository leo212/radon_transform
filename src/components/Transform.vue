<template>
    <div class="transformLayout">
        <div class="transformDiv">
            <md-field>
                <label for="algorithm">Radon Algorithm</label>
                <md-select
                    v-model="selectedAlgorithm"
                    name="algorithm"
                    id="algorithm"
                    @md-selected="variant = 'default'"
                >
                    <md-option value="dss">Direct Slant Stack</md-option>
                    <md-option value="pbim">Parallel Beams Image Rotation</md-option>
                    <md-option value="shas">Shift and Sum</md-option>
                    <md-option value="twoscale">Two-Scale Recursion</md-option>
                    <md-option value="sss">Slow Slant Stack</md-option>
                    <md-option value="fss">Fast Slant Stack</md-option>
                </md-select>
            </md-field>
            <md-field v-if="selectedAlgorithm === 'shas'">
                <label for="variant">Variant</label>
                <md-select v-model="variant" name="variant" id="variant">
                    <md-option value="default">Default</md-option>
                    <md-option v-if="selectedAlgorithm === 'shas'" value="cv2">CV2</md-option>
                </md-select>
            </md-field>
            <md-button class="transformButton md-raised md-primary" :disabled="animate" @click="runTransform()"
                >Transform</md-button
            >
        </div>
        <div class="transformPics">
            <div class="sourceHolder">
                <img ref="sourceImage" class="source" :src="filename" :alt="name" @load="imageLoaded" />
            </div>
            <div class="targetHolder">
                <div v-if="started" class="target">
                    <img class="target" :src="targetFilename + '?v=' + new Date().getTime()" :alt="name" />
                    <md-progress-bar md-mode="determinate" :md-value="progress"></md-progress-bar>
                </div>
                <md-empty-state
                    v-else
                    class="beforeTransform"
                    md-icon="assistant"
                    md-label="Transform hasn't started yet"
                    md-description="Choose an algorithm and click 'Transform' to start performing radon transform"
                />
            </div>
            <div class="transformInfo">
                <md-toolbar :md-elevation="1">
                    <span class="md-title">Information</span>
                </md-toolbar>

                <md-list class="md-double-line">
                    <md-subheader>Filename: {{ name }}</md-subheader>
                    <md-subheader>Image Dimensions: {{ width }} x {{ height }}</md-subheader>

                    <md-divider></md-divider>
                    <md-subheader>Transform information:</md-subheader>

                    <md-list-item>
                        <div class="md-list-item-text">
                            <span>Time elapsed: </span>
                            <span>{{ minutesElapsed }}:{{ secondsElapsed }}.{{ millisecondsElapsed }}</span>
                        </div>
                        <div class="md-list-item-text">
                            <span>Time remaining: </span>
                            <span>{{ minutesRemaining }}:{{ secondsRemaining }}.{{ millisecondsRemaining }}</span>
                        </div>
                    </md-list-item>

                    <md-list-item>
                        <div class="md-list-item-text">
                            <span
                                >Radon Cond:
                                <md-tooltip>Higher value means it will be harder to reconstruct</md-tooltip></span
                            >
                            <span>{{ cond }}</span>
                        </div>
                    </md-list-item>
                </md-list>
            </div>
        </div>
        <md-button class="md-raised md-accent" @click="closeTransform()">Close</md-button>
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
let server = require("../js/app.server");
let requestId = 0;

export default {
    name: "Transform",
    data: () => {
        return {
            width: 0,
            height: 0,
            imageWidth: 0,
            imageHeight: 0,
            selectedAlgorithm: "dss",
            variant: "default",
            progress: 0,
            started: false,
            targetFilename: "",
            animate: false,
            error: "",
            showSnackbar: false,
            minutesElapsed: "00",
            secondsElapsed: "00",
            millisecondsElapsed: "000",
            minutesRemaining: "00",
            secondsRemaining: "00",
            millisecondsRemaining: "000",
            cond: 0
        };
    },
    props: ["filename", "name"],
    mounted: function() {
        this.$data.imageWidth = this.$refs.sourceImage.width;
        this.$data.imageHeight = this.$refs.sourceImage.height;
    },

    methods: {
        imageLoaded() {
            this.$data.width = this.$refs.sourceImage.naturalWidth;
            this.$data.height = this.$refs.sourceImage.naturalHeight;
        },
        runTransform() {
            let data = this.$data;

            data.animate = true;
            data.started = true;

            // run radon transform service on server
            let checkStatusFunc = function() {
                server.checkJobStatus(requestId).then(status => {
                    // update progress and time passed
                    data.progress = status.progress;
                    data.minutesElapsed = Math.trunc(status.took / 1000 / 60)
                        .toString()
                        .padStart(2, "0");
                    data.secondsElapsed = Math.trunc((status.took / 1000) % 60)
                        .toString()
                        .padStart(2, "0");
                    data.millisecondsElapsed = Math.trunc(status.took % 1000)
                        .toString()
                        .padStart(3, "0");

                    // estimate time remaining
                    let remaining = (100 / status.progress) * status.took - status.took;
                    data.minutesRemaining = Math.trunc(remaining / 1000 / 60)
                        .toString()
                        .padStart(2, "0");
                    data.secondsRemaining = Math.trunc((remaining / 1000) % 60)
                        .toString()
                        .padStart(2, "0");
                    data.millisecondsRemaining = Math.trunc(remaining % 1000)
                        .toString()
                        .padStart(3, "0");

                    data.cond = status.cond;

                    // if the process hasn't ended it, check it again within 500ms
                    if (data.progress < 100) setTimeout(checkStatusFunc, 200);
                    else data.animate = false;
                });
            };

            server
                .runTransform(this.$data.selectedAlgorithm, this.$props.name, this.$data.variant)
                .then(json => {
                    requestId = json.requestId;
                    // set target filename
                    data.targetFilename = server.getResultFileUrl(json.target);
                    // start an interval to check the job status until it will be completed
                    setTimeout(checkStatusFunc, 200);
                })
                .catch(error => {
                    data.started = false;
                    data.animate = false;
                    data.error = "Server Error: " + error;
                    data.showSnackbar = true;
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

.transformDiv {
    display: flex;
    flex-direction: row;
}

.transformButton {
    width: 320px;
}

.transformInfo {
    width: 320px;
    max-width: 100%;
    margin: 8px;
    display: inline-block;
    vertical-align: top;
    overflow: auto;
    border: 1px solid rgba(#000, 0.12);
}

.progress {
}
</style>
