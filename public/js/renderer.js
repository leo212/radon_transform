// query from server
require('./config.js');

fetch(`http://${SERVER_HOST}/test`).then((result) => {
    result.text().then((resultText) => {
        document.getElementById('pythonResult').innerText = resultText;
    });
});