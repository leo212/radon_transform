<template>
    <div>
        <md-tabs class="md-primary" md-alignment="left" :md-active-tab="activeTab">
            <md-tab id="tab-home" md-label="Home" md-icon="home"><Home v-on:transform="transform"/></md-tab>
            <md-tab v-for="image in images" :md-label="image.name" :key="image.name" :id="image.name" md-icon="image">
                <Transform :filename="image.url" :name="image.name" v-on:closeTab="closeTab"></Transform>
            </md-tab>
        </md-tabs>
    </div>
</template>

<script>
import Home from "./components/Home";
import Transform from "./components/Transform";

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
        closeTab(key) {
            this.$data.activeTab = "tab-home";
            this.$data.images = this.$data["images"].filter(image => image.name !== key);
            delete openedTabs[key];
        }
    },
    components: {
        Transform,
        Home
    }
};
</script>
