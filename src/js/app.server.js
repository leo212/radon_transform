module.exports = {
    PYTHON_SERVER_URL: "http://localhost:8000",
    GET_IMAGE_SERVICE: "/get_image/",
    GET_IMAGE_RESULT_SERVICE: "/get_result/",
    GET_IMAGE_LIST_SERVICE: "/get_filelist/",
    TRANSFORM_SERVICE: "/transform/",
    GET_STATUS_SERVICE: "/get_job_status/",
    SERVER_STATUS_SERVICE: "/test/",

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

    runTransform: function(algorithm, filename) {
        return new Promise((resolve, reject) => {
            fetch(this.PYTHON_SERVER_URL + this.TRANSFORM_SERVICE + algorithm + "/" + filename).then(response => {
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
    }
};
