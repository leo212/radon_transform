export default {
    PYTHON_SERVER_URL: "http://localhost:8000",
    GET_IMAGE_SERVICE: "/get_image/",
    GET_IMAGE_RESULT_SERVICE: "/get_result/",
    GET_IMAGE_RECONSTRUCTED_SERVICE: "/get_reconstructed/",
    GET_IMAGE_LIST_SERVICE: "/get_filelist/uploaded",
    GET_RESULT_LIST_SERVICE: "/get_filelist/result",
    TRANSFORM_SERVICE: "/transform/",
    RECONSTRUCT_SERVICE: "/reconstruct/",
    BUILD_MATRIX_SERVICE: "/build_matrix/",
    IS_MATRIX_AVAILABLE_SERVICE: "/is_matrix_available/",
    GET_STATUS_SERVICE: "/get_job_status/",
    SERVER_STATUS_SERVICE: "/test/",
    TRANSFORM_TYPES: [
        { key: "dss", name: "Direct Slant Stack" },
        { key: "pbim", name: "Parallel Beams Image Rotation" },
        { key: "shas", name: "Shift and Sum" },
        { key: "twoscale", name: "Two-Scale Recursion" },
        { key: "sss", name: "Slow Slant Stack" },
        { key: "fss", name: "Fast Slant Stack" }
    ],

    // check status of python server
    checkStatus: function() {
        return new Promise((resolve, reject) => {
            fetch(this.PYTHON_SERVER_URL + this.SERVER_STATUS_SERVICE)
                .then(response => {
                    if (response.ok) {
                        resolve();
                    } else {
                        reject("HTTP Response error");
                    }
                })
                .catch(error => {
                    reject(error);
                });
        });
    },

    getImageList: function(files) {
        fetch(this.PYTHON_SERVER_URL + this.GET_IMAGE_LIST_SERVICE).then(response => {
            if (response.ok) {
                response.json().then(json => {
                    let fileList = json["file_list"];
                    for (let index in fileList) {
                        // noinspection JSUnfilteredForInLoop
                        let image = fileList[index];
                        files.push({
                            url: this.PYTHON_SERVER_URL + this.GET_IMAGE_SERVICE + image,
                            name: image,
                            uploaded: true
                        });
                    }
                });
            }
        });
    },

    getRadonList: function(files) {
        fetch(this.PYTHON_SERVER_URL + this.GET_RESULT_LIST_SERVICE).then(response => {
            if (response.ok) {
                response.json().then(json => {
                    let fileList = json["file_list"];
                    for (let index in fileList) {
                        // noinspection JSUnfilteredForInLoop
                        let image = fileList[index];
                        let file = {
                            url: this.PYTHON_SERVER_URL + this.GET_IMAGE_RESULT_SERVICE + image,
                            name: image,
                            uploaded: true
                        };

                        let parts = image.match(/(.*)\.(.*)\.(.*)\.(.*)/);

                        if (parts.length >= 5) {
                            file["algorithm"] = parts[2];
                            file["variant"] = parts[3];
                        }
                        files.push(file);
                    }
                });
            }
        });
    },

    checkJobStatus: function(requestId) {
        return new Promise(resolve => {
            fetch(this.PYTHON_SERVER_URL + this.GET_STATUS_SERVICE + requestId).then(response => {
                if (response.ok) {
                    response.json().then(json => {
                        resolve(json);
                    });
                }
            });
        });
    },

    runTransform: function(algorithm, filename, variant) {
        return new Promise((resolve, reject) => {
            fetch(this.PYTHON_SERVER_URL + this.TRANSFORM_SERVICE + algorithm + "/" + variant + "/" + filename).then(
                response => {
                    if (response.ok) {
                        response.json().then(json => {
                            if (!json.error) {
                                resolve(json);
                            } else {
                                reject(json.error);
                            }
                        });
                    }
                }
            );
        });
    },

    runBuildMatrix: function(algorithm, variant, size) {
        return new Promise((resolve, reject) => {
            fetch(this.PYTHON_SERVER_URL + this.BUILD_MATRIX_SERVICE + algorithm + "/" + variant + "/" + size).then(
                response => {
                    if (response.ok) {
                        response.json().then(json => {
                            if (!json.error) {
                                resolve(json);
                            } else {
                                reject(json.error);
                            }
                        });
                    }
                }
            );
        });
    },

    checkIfMatrixAvailable: function(algorithm, variant, size) {
        return new Promise((resolve, reject) => {
            fetch(
                this.PYTHON_SERVER_URL + this.IS_MATRIX_AVAILABLE_SERVICE + algorithm + "/" + variant + "/" + size
            ).then(response => {
                if (response.ok) {
                    response.json().then(json => {
                        if (!json.error) {
                            resolve(json["matrixAvailable"]);
                        } else {
                            reject(json.error);
                        }
                    });
                }
            });
        });
    },

    runReconstruct: function(filename, method) {
        return new Promise((resolve, reject) => {
            fetch(this.PYTHON_SERVER_URL + this.RECONSTRUCT_SERVICE + method + "/" + filename).then(response => {
                if (response.ok) {
                    response.json().then(json => {
                        if (!json.error) {
                            resolve(json);
                        } else {
                            reject(json.error);
                        }
                    });
                }
            });
        });
    },

    getImageFileUrl: function(filename) {
        return this.PYTHON_SERVER_URL + this.GET_IMAGE_SERVICE + filename;
    },

    getResultFileUrl: function(filename) {
        return this.PYTHON_SERVER_URL + this.GET_IMAGE_RESULT_SERVICE + filename;
    },

    getReconstructedFileUrl: function(filename) {
        return this.PYTHON_SERVER_URL + this.GET_IMAGE_RECONSTRUCTED_SERVICE + filename;
    }
};
