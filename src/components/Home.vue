<template>
  <div>
    Python Server Status: {{ serverStatus }}
    <md-icon v-if="serverStatus === 'OK'">check</md-icon>
    <md-icon v-if="serverStatus === 'FAIL'">error</md-icon>
  </div>
</template>

<script>
let data = {
  serverStatus: "Checking..."
};

export default {
  data: function() {
    return data;
  }
};

fetch("http://localhost:8000/test")
  .then(response => {
    if (response.ok) {
      data.serverStatus = "OK";
    } else {
      data.serverStatus = "N/A";
    }
  })
  .catch(() => {
    data.serverStatus = "FAIL";
  });
</script>
