<script setup>
import { ref } from 'vue';

import {host, protocol, 
        str2pos, pos2str, lpos, pos, hpos,
        section_type,
        sections,section,
        movies, movie,
        seasons,season,
        series, serie,
        get_frame,
        frame_name,
        pos2fname,
        toggle_timeline,
        ltimeline
} from '@/app';

const style_shift_down = ref("top: calc(2*49px);")
</script>

<!-- place the v-img component below the components listed in front of this one in app.vue -->

<template>
    <div class="dbox dbox-main-detail" v-if="toggle_timeline">
            <v-img
            v-for="ival in ltimeline.larray"
            :style = "style_shift_down"
            :key="ival"
            @click="hpos({val: ival, type:'abs'})"
            :src="pos2fname(ival)" 
            class="mx-auto" 
            >
        </v-img>  
    </div>
    <div class="dbox dbox-main">
        <v-img 
        :style = "style_shift_down"
        class="mx-0"
        :src="frame_name" 
        alt="... loading ..."
        >
    </v-img>
</div>
<v-card
    :style = "style_shift_down"
>
    <v-card-title>
        <v-row>
            <v-col cols="12">
                toggle_timeline {{ toggle_timeline }}
            </v-col>
        </v-row>
    </v-card-title>         
</v-card>
</template> 

<style scoped>
.dbox {
    display: flex;
    justify-content: center;
    align-items: center;
}

.dbox-main-detail {
    flex-direction: row;
    justify-content: stretch;
    background: var(--bg-pic);
    grid-column: 1;
    grid-row: 1;
}

.dbox-main {
    background: var(--bg-pic);
    grid-column: 1;
    grid-row: 2;
}
.frame {
    min-width: 50%;
    max-width: 100%;
    height: auto;
}
</style>