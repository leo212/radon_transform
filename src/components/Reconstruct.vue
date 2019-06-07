<template>
    <div class="transformLayout">
        <div class="transformDiv">
            <div class="algorithm-name md-title">
                Radon Algorithm
                <div class="md-subheading">{{ getAlgorithmName(algorithm) }}</div>
            </div>
            <div class="runMatrixBuildButton">
                <md-button
                    class="buildMatrixButton md-raised md-primary"
                    :disabled="matrixProgress > 0"
                    @click="buildMatrix()"
                    >Build Matrix</md-button
                >
                <md-progress-bar
                    md-mode="determinate"
                    :md-value="matrixProgress"
                    class="buildMatrixProgress"
                ></md-progress-bar>
            </div>
            <div class="reconstructButton">
                <md-button
                    class="reconstructButton md-raised md-primary"
                    :disabled="animate || !matrixBuilt"
                    @click="runReconstruct()"
                    >Reconstruct
                </md-button>
                <md-tooltip v-if="!matrixBuilt"
                    >Radon matrix need to be built for this image size before running construction</md-tooltip
                >
            </div>
        </div>
        <div class="transformPics">
            <div v-if="started || reconstructed" class="imageHolder">
                <div class="md-subheader">Original Image</div>
                <img ref="originalImage" class="source" :src="originalFilename" :alt="name" @load="imageLoaded" />
            </div>
            <div class="imageHolder">
                <div class="md-subheader">Radon Transform</div>
                <img ref="sourceImage" class="source" :src="filename" :alt="name" @load="imageLoaded" />
            </div>
            <div v-if="reconstructed" class="imageHolder">
                <div class="md-subheader">Reconstructed Image</div>
                <img class="target" :src="targetFilename + '?v=' + new Date().getTime()" :alt="name" />
            </div>
            <div v-if="!reconstructed" class="targetHolder">
                <md-empty-state
                    v-if="!matrixBuilt"
                    class="beforeReconstruct"
                    md-icon="assistant"
                    md-label="Reconstruction Matrix is not Available"
                    md-description="Click 'Build Matrix' to start building a reconstruction matrix (it should take a while)"
                />
                <md-empty-state
                    v-else
                    class="beforeReconstruct"
                    md-icon="assistant"
                    md-label="Reconstruct hasn't started yet"
                    md-description="Click 'Reconstruct' to reconstruct the image from the radon transform"
                />
            </div>
            <div class="reconstructInfo">
                <md-toolbar :md-elevation="1">
                    <span class="md-title">Information</span>
                </md-toolbar>

                <md-list class="md-double-line">
                    <md-subheader>Filename: {{ name }}</md-subheader>
                    <md-divider></md-divider>
                    <md-subheader>Image Dimensions: {{ width }} x {{ height }}</md-subheader>
                    <md-divider></md-divider>
                    <md-subheader>Reconstruction Matrix Available: {{ matrixBuilt }}</md-subheader>
                    <md-divider></md-divider>
                    <md-subheader>Reconstruct information:</md-subheader>

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
        <md-button class="md-raised md-accent" @click="closeReconstruct()">Close</md-button>
        <md-snackbar :md-active.sync="showSnackbar" md-persistent>
            <span>{{ error }}</span>
            <md-button
                class="md-primary"
                @click="
                    showSnackbar = false;
                    runReconstruct();
                "
                >Retry</md-button
            >
        </md-snackbar>
        <div></div>
    </div>
</template>

<script>
import server from "../js/app.server";
let requestId = 0;

export default {
    name: "Reconstruct",
    data: () => {
        return {
            matrixBuilt: false,
            width: 0,
            height: 0,
            imageWidth: 0,
            imageHeight: 0,
            progress: 0,
            matrixProgress: 0,
            started: false,
            reconstructed: false,
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
            cond: 0,
            transformTypes: server.TRANSFORM_TYPES,
            originalFilename: ""
        };
    },
    props: ["filename", "name", "algorithm", "variant"],
    mounted: function() {
        this.$data.imageWidth = this.$refs.sourceImage.width;
        this.$data.imageHeight = this.$refs.sourceImage.height;
    },

    methods: {
        imageLoaded() {
            this.$data.width = this.$refs.sourceImage.naturalWidth;
            this.$data.height = this.$refs.sourceImage.naturalHeight;
        },
        getAlgorithmName(key) {
            let algorithm = server.TRANSFORM_TYPES.filter(type => type.key === key);
            if (algorithm.length > 0) {
                return algorithm[0].name;
            } else {
                return "Unknown";
            }
        },
        buildMatrix() {
            let data = this.$data;

            // run radon transform service on server
            let checkStatusFunc = function() {
                server.checkJobStatus(requestId).then(status => {
                    // update progress and time passed
                    data.matrixProgress = status.progress;
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

                    // if the process hasn't ended it, check it again within 500ms
                    if (data.matrixProgress < 100) setTimeout(checkStatusFunc, 200);
                    else {
                        data.matrixBuilt = true;
                    }
                });
            };

            server
                .runBuildMatrix(this.$props.algorithm, this.$props.variant, this.$data.width)
                .then(json => {
                    requestId = json.requestId;
                    // start an interval to check the job status until it will be completed
                    setTimeout(checkStatusFunc, 200);
                })
                .catch(error => {
                    data.error = "Server Error: " + error;
                    data.showSnackbar = true;
                });
        },
        runReconstruct() {
            let data = this.$data;

            // run radon transform service on server
            let checkStatusFunc = function() {
                server.checkJobStatus(requestId).then(status => {
                    // update progress and time passed
                    data.matrixProgress = status.progress;
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

                    data.progress = status.progress;
                    // if the process hasn't ended it, check it again within 500ms
                    if (status.status !== "completed") setTimeout(checkStatusFunc, 200);
                    else {
                        data.reconstructed = true;
                        data.started = false;
                    }
                });
            };

            server
                .runReconstruct(this.$props.name)
                .then(json => {
                    requestId = json.requestId;
                    // start an interval to check the job status until it will be completed
                    setTimeout(checkStatusFunc, 200);
                    data.started = true;
                    data.targetFilename = server.getReconstructedFileUrl(json.target);
                    data.originalFilename = server.getImageFileUrl(json.target);
                })
                .catch(error => {
                    data.error = "Server Error: " + error;
                    data.showSnackbar = true;
                });
        },
        closeReconstruct() {
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
    justify-content: space-between;
}

.imageHolder {
    display: flex;
    flex-direction: column;
    flex: 1;
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
    flex: 1;
    padding: 8px;
    max-width: 512px;
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.emptyImage {
    background: black;
    flex: 1;
}

.target {
    flex: 1;
    padding: 8px;
    max-width: 512px;
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.beforeReconstruct {
    transition: none;
}

.transformDiv {
    display: flex;
    flex-direction: row;
}

.reconstructButton {
    width: 200px;
    height: 36px;
}

.buildMatrixButton {
    width: 320px;
}

.reconstructInfo {
    width: 320px;
    max-width: 100%;
    margin: 8px;
    display: inline-block;
    vertical-align: top;
    overflow: auto;
    border: 1px solid rgba(#000, 0.12);
}

.algorithm-name {
    flex: 1;
}

.runMatrixBuildButton {
    display: flex;
    flex-direction: column;
}

.buildMatrixProgress {
    margin-left: 8px;
    margin-right: 8px;
}

.progress {
}
</style>