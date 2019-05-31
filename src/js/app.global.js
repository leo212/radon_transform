module.exports = {
    loadCss: function(cssId) {
        if (!document.getElementById(cssId)) {
            const head = document.getElementsByTagName("head")[0];
            const link = document.createElement("link");
            link.id = cssId;
            link.rel = "stylesheet";
            link.type = "text/css";
            link.href = cssId;
            link.media = "all";
            head.appendChild(link);
        }
    }
};
