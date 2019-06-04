<template>
    <div class="transformLayout">
        <div class="transformDiv">
            <div class="algorithm-name md-title">
                Radon Algorithm
                <div class="md-subheading">{{ getAlgorithmName(algorithm) }}</div>
            </div>
            <md-button class="buildMatrixButton md-raised md-primary" :disabled="animate" @click="buildMatrix()"
                >Build Matrix</md-button
            >
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
            <div class="sourceHolder">
                <img ref="sourceImage" class="source" :src="filename" :alt="name" @load="imageLoaded" />
            </div>
            <div class="targetHolder">
                <div v-if="started" class="target">
                    <img class="target" :src="targetFilename + '?v=' + new Date().getTime()" :alt="name" />
                    <md-progress-bar md-mode="determinate" :md-value="progress"></md-progress-bar>
                </div>
                <md-empty-state
                    v-else-if="!matrixBuilt"
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
            cond: 0,
            transformTypes: server.TRANSFORM_TYPES
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
            this.$data.matrixBuilt = true;
        },
        runReconstruct() {
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

.progress {
}
</style>
