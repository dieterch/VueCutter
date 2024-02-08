<script setup>
import { ref, computed } from 'vue'
import axios from 'axios';

import {host, protocol, str2pos, lpos, 
        section_type,
        sections,section,
        movies, movie,
        seasons,season,
        series, serie, 
        toggle_timeline, 
        timeline, 
        reset_t0_t1
} from '@/app';

// methods:
async function load_selection() {
    const endpoint = `${protocol.value}//${host.value}/selection`
    try {
        const response = await axios.get(endpoint, { headers: { 'Content-type': 'application/json', }});
        sections.value = response.data.sections;
        section.value = response.data.section;
        section_type.value = response.data.section_type;
        movies.value = response.data.movies;
        movie.value = response.data.movie;
        seasons.value = response.data.seasons;
        season.value = response.data.season;
        series.value = response.data.series;
        serie.value = response.data.serie;
        lpos.value = str2pos(response.data.pos_time)
        onChangeMovie()
    } catch (e) {
        console.log(`${endpoint} \n` + String(e));
        alert(`${endpoint} \n` + String(e));
    }
}

async function update_section( sec ) {
    const endpoint = `${protocol.value}//${host.value}/update_section`
    section.value = sec;
    try {
        const response = await axios.post(endpoint,
            { "section": section.value },
            { headers: { 'Content-type': 'application/json', }});
            load_selection();
    } catch (e) {
        console.log(`${endpoint} \n` + String(e));
        alert(`${endpoint} \n` + String(e));
    }
}

async function update_serie() {
    const endpoint = `${protocol.value}//${host.value}/update_serie`
    try {
        const response = await axios.post(endpoint,
            { "serie": serie.value },
            { headers: { 'Content-type': 'application/json', }});
            load_selection();
    } catch (e) {
        console.log(`${endpoint} \n` + String(e));
        alert(`${endpoint} \n` + String(e));
    }
} 

async function update_season() {
    const endpoint = `${protocol.value}//${host.value}/update_season`
    try {
        const response = await axios.post(endpoint,
            { "season": season.value },
            { headers: { 'Content-type': 'application/json', }});
            load_selection();
    } catch (e) {
        console.log(`${endpoint} \n` + String(e));
        alert(`${endpoint} \n` + String(e));
    }
}

function onChangeMovie() {
    reset_t0_t1()
    toggle_timeline.value = false
    console.log("onChangeMovie")
}   


import { useTheme } from 'vuetify'

const theme = useTheme()

function setTheme (themeName) { 
  theme.global.name.value = themeName
}

function filterTheme (themeName) {
  return ((themeName[0] != 'dark') & (themeName[0] != 'light'))
}


load_selection() // initial load
</script>

<template>
    <v-app-bar
        name="menu-bar" 
        color="toolsbackground"
        density="compact"
        :elevation="0"
    >
        <template v-slot:prepend>

            <v-menu location="bottom">
                <template v-slot:activator="{ props }">
                    <v-app-bar-nav-icon
                    v-bind="props"
                    size="small"
                    >
                    </v-app-bar-nav-icon>
                </template>
                <v-list
                    density="compact"
                >
                    <v-list-item
                    v-for="(sec, index) in sections"
                    :key="index"
                    >
                    <v-list-item-title
                        @click="update_section(sec)"
                    >{{ sec }}</v-list-item-title>
                    </v-list-item>
                </v-list>
            </v-menu>

            <v-app-bar-title>Vue Web Cutter</v-app-bar-title>

        </template>

        <template v-slot:default>
            <v-select
                v-if="section_type == 'show'"
                class="mt-6 ml-2 mr-0"
                :label="`${series.length} Series`"
                v-model="serie"
                :model-value="serie"
                density="compact"
                :items="series"
                variant="solo"
                @update:model-value="update_serie"
            ></v-select>

            <v-select
                v-if="section_type == 'show'"
                class="mt-6 ml-2 mr-0"
                :label="`${seasons.length} Seasons`"
                v-model="season"
                :model-value="season"
                density="compact"
                :items="seasons"
                variant="solo"
                @update:model-value="update_season"
            ></v-select>

            <v-select
                class="mt-6 ml-2 mr-2"
                :label="`${section} - ${movies.length} movies`"
                v-model="movie"
                :model-value="movie"
                density="compact"
                :items="movies"
                variant="solo"
                @update:model-value="onChangeMovie"
            ></v-select>

        </template>

        <template v-slot:append>
            <v-btn icon="mdi-reload" href="/force_update_section" size="small"></v-btn>
            <v-btn icon="mdi-dots-vertical" href="/streamurl.xspf" size="small"></v-btn>
            <v-menu location="bottom">
                <template v-slot:activator="{ props }">
                    <v-btn icon="mdi-palette-swatch" @click="toggleTheme" v-bind="props" size="small"></v-btn>
                </template>
                <v-list
                    density="compact"
                >
                        <v-list-item
                            v-for="[key, value] of Object.entries(theme.themes.value).filter(filterTheme)"
                            v-bind="props"
                            :key="key"
                            :color="isHovering ? 'primary' : 'transparent'"
                            >
                            <v-list-item-title
                                @click="setTheme(key)"
                            >{{ key }}</v-list-item-title>
                        </v-list-item>
                </v-list>
            </v-menu>            
        </template>
    </v-app-bar>

</template>
