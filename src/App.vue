<template>
    <div>
        <md-tabs class="md-primary" md-alignment="left" :md-active-tab="activeTab" v-on:md-changed="changedTab">
            <md-tab id="tab-home" md-label="Home" md-icon="home">
                <Home ref="home" v-on:transform="transform" v-on:reconstruct="reconstruct" />
            </md-tab>
            <md-tab v-for="image in images" :md-label="image.name" :key="image.name" :id="image.name" md-icon="image">
                <Reconstruct
                    v-if="image.reconstruct"
                    :filename="image.url"
                    :name="image.name"
                    :algorithm="image.algorithm"
                    :variant="image.variant"
                    v-on:closeTab="closeTab"
                />
                <Transform v-else :filename="image.url" :name="image.name" v-on:closeTab="closeTab" />
            </md-tab>
        </md-tabs>
    </div>
</template>

<script>
import Home from "./components/Home";
import Transform from "./components/Transform";
import Reconstruct from "./components/Reconstruct";

let openedTabs = {};

export default {
    data: () => {
        return {
            images: [],
            activeTab: "tab-home"
        };
    },
    methods: {
        transform(file) {
            if (!openedTabs[file.name]) {
                openedTabs[file.name] = true;
                this.$data.images.push(file);
            }
            this.$data["activeTab"] = file.name;
        },
        reconstruct(file) {
            if (!openedTabs[file.name]) {
                openedTabs[file.name] = true;
                file.reconstruct = true;
                this.$data.images.push(file);
            }
            this.$data["activeTab"] = file.name;
        },
        closeTab(key) {
            this.$data.activeTab = "tab-home";
            this.$data.images = this.$data["images"].filter(image => image.name !== key);
            delete openedTabs[key];
        },
        changedTab(key) {
            // if switch back to home
            if (key === "tab-home") {
                // reconnect to server and update file list
                this.$refs.home.connectToServer();
            }
        }
    },
    components: {
        Reconstruct,
        Transform,
        Home
    }
};
</script>
