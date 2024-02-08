<script setup>
import { ref, computed } from 'vue'
import { 
    movies, movie, 
    lmovie_info,
    pos, lpos, hpos, posvalid,
    pos_from_end, pos2str,  
    timeline, ltimeline, toggle_timeline
} from '@/app';

const buttons_left = computed(() => {
    return [
        {name:"", icon:'mdi-format-horizontal-align-left', val:0, type:"abs", color:"primary-button"},
        {name:" 15'", icon:'mdi-format-horizontal-align-left', val:15*60, type:"abs", color:"primary-button"},
        {name:" 30'", icon: 'mdi-arrow-left-thin', val:-1800, type:"rel", color:"secondary-button"},
        {name:" 10'", icon: 'mdi-arrow-left-thin', val:-600, type:"rel", color:"secondary-button"},
        {name:" 5'", icon: 'mdi-arrow-left-thin', val:-5*60, type:"rel", color:"secondary-button"},
        {name:" 1'", icon: 'mdi-arrow-left-thin', val:-60, type:"rel", color:"secondary-button"},
        {name:' 10"', icon: 'mdi-arrow-left-thin', val:-10, type:"rel", color:"tertiary-button"},
        {name:' 5"', icon: 'mdi-arrow-left-thin', val:-5, type:"rel", color:"tertiary-button"},
        {name:' 1"', icon: 'mdi-arrow-left-thin', val:-1, type:"rel", color:"tertiary-button"},
    ]
})

const buttons_right = computed(() => {
    return [
        {name:'1" ', icon: 'mdi-arrow-right-thin', val:1, type:"rel", color:"tertiary-button"},
        {name:'5" ', icon: 'mdi-arrow-right-thin', val:5, type:"rel", color:"tertiary-button"},                    
        {name:'10" ', icon: 'mdi-arrow-right-thin', val:10, type:"rel", color:"tertiary-button"},                    
        {name:"1' ", icon: 'mdi-arrow-right-thin', val:60, type:"rel", color:"secondary-button"},
        {name:"5' ", icon: 'mdi-arrow-right-thin', val:5*60, type:"rel", color:"secondary-button"},
        {name:"10' ", icon: 'mdi-arrow-right-thin', val:600, type:"rel", color:"secondary-button"},
        {name:"30' ", icon: 'mdi-arrow-right-thin', val:1800, type:"rel", color:"secondary-button"},
        {name:"15' ",icon: 'mdi-format-horizontal-align-right', val:pos_from_end(15*60), type:"abs", color:"primary-button"},
        {name:"",icon: 'mdi-format-horizontal-align-right', val:pos_from_end(0), type:"abs", color:"primary-button"},
    ]
})


function page_minus_timeline() {
    if (lpos.value + ((ltimeline.value.l - ltimeline.value.r) * ltimeline.value.step)> 0) {
        lpos.value += (ltimeline.value.l - ltimeline.value.r) * ltimeline.value.step
        lpos.value = posvalid(lpos.value)                
    } else lpos.value = 0
    timeline(lpos.value)
}

function page_plus_timeline() {
    //console.log('in ">":',this.lpos, this.pos_from_end(0), this.lpos + (this.ltimeline.r - this.ltimeline.l) * this.ltimeline.step)
    if (lpos.value + ((ltimeline.value.r - ltimeline.value.l) * ltimeline.value.step ) < pos_from_end(0)) {
        lpos.value += (ltimeline.value.r - ltimeline.value.l) * ltimeline.value.step
        //console.log('in ">, if ... nach +=":',this.lpos)
        lpos.value = posvalid(lpos.value)
        //console.log('in ">, if ... nach this.posvalid":',this.lpos)
    } else lpos.value = pos_from_end(0)
    timeline(lpos.value)
}

function toggle_and_timeline(mypos) {
    let tlt = toggle_timeline.value
    toggle_timeline.value = !tlt
    lpos.value = posvalid(lpos.value)
    // console.log('in "toggle_and_timeline":',mypos)
    timeline(mypos)
}
</script>

<template>
    <v-navigation-drawer
        name="side-bar"
        permanent
        location="right"
        color="toolsbackground"
        :width="160"
    >
        <v-row 
            justify="center"
            class="py-2 px-2">
                <v-col cols="4">
                    <v-btn 
                        no-density="comfortable" 
                        icon="mdi-arrow-left-bold-box-outline" 
                        class=""
                        color="primary-button"
                        size="x-small"
                        variant="flat"
                        @click="page_minus_timeline()"
                    ></v-btn>
                </v-col>
                <v-col cols="4">
                    <v-btn 
                        no-density="comfortable" 
                        icon="mdi-filmstrip" 
                        class=""
                        color="primary-button"
                        size="x-small"
                        variant="flat"
                        @click="toggle_and_timeline(lpos)"
                    ></v-btn>
                </v-col>
                <v-col cols="4">
                    <v-btn 
                        no-density="comfortable" 
                        icon="mdi-arrow-right-bold-box-outline" 
                        class=""
                        color="primary-button"
                        size="x-small"
                        variant="flat"
                        @click="page_plus_timeline()"
                    ></v-btn>
                </v-col>
        </v-row>
        <div class="no-text-center">
            <v-chip 
                prepend-icon="mdi-movie-open" 
                label
                variant="text"
                size="default"
                class="mt-2 ml-2"
                >
                <strong>{{ pos2str(lmovie_info.duration * 60) }} &nbsp;&nbsp;&nbsp; ({{ lmovie_info.duration }}')</strong>
            </v-chip>
            <v-chip 
                prepend-icon="mdi-movie-open-edit" 
                variant="text"
                label
                size="default"
                class="mt-0 ml-2"
                >
                <strong>
                    {{ pos }} &nbsp;&nbsp;&nbsp; ({{ Math.trunc(lpos / 60) }}')
                </strong>
            </v-chip>
    </div>
<v-divider></v-divider>
<div class="sb_container">
            <div 
                class="sb_box sb_box-buttons1 mt-2"
            >
                <v-btn 
                    v-for="b in buttons_left"
                    :prepend-icon="b.icon"
                    :color="b.color"
                    class="ma-1" 
                    width="65px"
                    @click="hpos(b)"
                    >
                    <span
                        :style="(-b.val == ltimeline.step) ? 'text-decoration: overline;' : 'text-decoration: none;'"                 
                    >
                        {{ b.name }}
                    </span>
                </v-btn>
            </div>
            
            <div class="sb_box sb_box-buttons2 mt-2">
                <v-btn 
                    v-for="b in buttons_right"
                    :append-icon="b.icon"
                    :color="b.color"
                    class="ma-1" 
                    width="65px"
                    @click="hpos(b)"
                    >
                    <span
                        :style="(b.val == ltimeline.step) ? 'text-decoration: overline;' : 'text-decoration: none;'"                 
                    >
                        {{ b.name }}
                    </span>
                </v-btn>
            </div>            
        </div>
    </v-navigation-drawer>
  </template>

<style scoped>
button {
  font-weight: bold;
}

/* sidebar grid */
.sb_container {
    display: grid;
    grid-template-rows: auto auto auto 100fr;
    grid-template-columns: 50fr 50fr;   
}

.sb_box {
    display: flex;
    justify-content: center;
    align-items: center;
}

.sb_box-buttons1 {
    flex-direction: column;
    grid-column: 1;
    grid-row: 4;
}

.sb_box-buttons2 {
    flex-direction:column-reverse;
    grid-column: 2;
    grid-row: 4;
}
/* sidebar grid */
</style>