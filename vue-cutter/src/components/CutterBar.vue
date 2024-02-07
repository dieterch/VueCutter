<script setup>
import { ref, computed } from 'vue'
import axios from 'axios';

import {
    protocol, host, 
    t0, t0_valid, 
    t1, t1_valid,
    inplace,
    ltimeline,
    movie, lmovie, section,
    hpos, progress_status } from '@/app';

const cut_ok = computed(() => {
        // console.log(t0_valid.value, t1_valid.value, ltimeline.value.step)
        return t0_valid.value & t1_valid.value & ( ltimeline.value.step == 1 )
    })

const inplaceIcon = computed(() => {
    let ret = (inplace.value) ? "mdi-toggle-switch-variant" :  "mdi-toggle-switch-variant-off"
    // console.log(ret)
    return ret
})

function toggle_inplace() {
        inplace.value = !inplace.value
    }

const lmovie_cut_info = ref({})
const dialog = ref(false);
const msg = ref('')

async function cut_info() {
    const endpoint = `${protocol.value}//${host.value}/movie_cut_info`
    try {
        const response = await axios.get(endpoint, { headers: { 'Content-type': 'application/json', }});
        lmovie_cut_info.value = response.data;
        //console.log("in movie_cut_info", this.lmovie_cut_info)
        msg.value = {
            section: section.value,
            movie: lmovie.value,
            In: t0.value,
            Out: t1.value,
            Inplace: inplace.value,
            ".ap .sc Files ?": lmovie_cut_info.value.apsc,
            "_cut File ?": lmovie_cut_info.value.cutfile
        }
        console.log(msg.value)
        dialog.value = true
    } catch (e) {
        console.log(`${endpoint} \n` + String(e));
        alert(`${endpoint} \n` + String(e));
    }
}

async function do_cut() {
    const endpoint = `${protocol.value}//${host.value}/cut2`
    try {
        const response = await axios.post(endpoint,
        {   
            "section": section.value, 
            "movie_name": lmovie.value,
            "ss": t0.value,
            "to": t1.value,
            "inplace": inplace.value,
            "etaest": lmovie_cut_info.value.eta
        },
        { headers: { 'Content-type': 'application/json',}});
        console.log(response.data)
        progress()
        dialog.value = false
    } catch (e) {
        console.log(`${endpoint} \n` + String(e));
        alert(`${endpoint} \n` + String(e));
    }
}

function progress() {
    const endpoint = `${protocol.value}//${host.value}/progress`
    let timer_id = setInterval( async () => {
        try {
            const response = await axios.get(endpoint, { headers: { 'Content-type': 'application/json', }});
            progress_status.value = response.data
            console.log(progress_status.value)
            if (progress_status.value.status == "idle") {
                console.log("done")
                clearInterval(timer_id)
            }
        } catch (e) {
            console.log(`${endpoint} \n` + String(e));
            alert(`${endpoint} \n` + String(e));
        }
    }, 5000)
    console.log("progress", timer_id)
}

</script>

<template>
    <v-dialog
    v-model="dialog"
    persistent="true"
    width="auto"
    >
        <v-card
            title="Cut Info"
            :subtitle="movie"
        >
            <v-card-text>
                <v-table density="compact">
                    <thead>
                        <tr>
                            <th class="text-left">Name</th>
                            <th class="text-left">Wert</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr
                        v-for = "(val, key) in msg"
                        :key = "key"
                        >
                            <td>{{ key }}</td>
                            <td>{{ val }}</td>
                        </tr>
                    </tbody>
                </v-table>
            </v-card-text>
            <v-divider></v-divider>
            <v-card-actions>
                <v-spacer/>
                <v-btn
                    class="ml-4"
                    color="error"
                    variant="flat"
                    prepend-icon="mdi-content-cut"
                    width="120px"
                    @click="do_cut"
                >
                Cut
                </v-btn>
                <v-btn
                    class="ml-4"
                    color="blue-darken-1"
                    variant="flat"
                    prepend-icon="mdi-cancel"
                    width="120px"
                    @click="dialog = false"
                >
                Cancel
                </v-btn>
                <v-spacer/>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <v-app-bar
    name="cutter-bar" 
    color="surface-light"
    density="compact"
    height="100px"
    :elevation="0"
    >
        <v-row dense justify="center" class="ma-1">
            <v-col>
                <v-btn
                    v-if="t0_valid"
                    variant="flat"
                    class=""
                    color="primary"
                    size="default"
                    prepend-icon="mdi-align-horizontal-right"
                    block="true"
                    @click="hpos({type:'t0'})"
                >
                {{ t0 }}
                </v-btn>
                <v-btn
                    v-else
                    variant="flat"
                    class=""
                    color="primary"
                    size="default"
                    prepend-icon="mdi-align-horizontal-right"
                    block="true"
                    @click="hpos({type:'t0'})"
                >
                -- : -- : --
                </v-btn>
            </v-col>

            <v-col>
                <v-btn
                    v-if="t1_valid"
                    variant="flat"
                    class="pr-2"
                    color="primary"
                    block="true"
                    size="default"
                    append-icon="mdi-align-horizontal-left"
                    @click="hpos({type:'t1'})"
                    >
                    {{ t1 }}
                </v-btn>
                <v-btn
                    v-else
                    variant="flat"
                    class="pr-2"
                    color="primary"
                    block="true"
                    size="default"
                    append-icon="mdi-align-horizontal-left"
                    @click="hpos({type:'t1'})"
                    >
                    -- : -- : --
                </v-btn>
            </v-col>
            
            <v-col>
                <v-btn
                    v-if="cut_ok"
                    variant="flat"
                    class=""
                    color="primary"
                    block="true"
                    size="default"
                    :append-icon=inplaceIcon
                    @click="toggle_inplace"
                >
                Inplace
                </v-btn>
                <v-btn
                    v-else
                    variant="flat"
                    class=""
                    color="tertiary"
                    block="true"
                    size="default"
                    :append-icon=inplaceIcon
                    disabled
                >
                Inplace
                </v-btn>
            </v-col>
        
            <v-col>
                <v-btn
                    v-if="cut_ok"
                    variant="flat"
                    class=""
                    color="error"
                    block="true"
                    size="default"
                    append-icon="mdi-content-cut"
                    @click="cut_info"
                >
                Cut
                </v-btn>
                <v-btn
                    v-else
                    variant="flat"
                    class=""
                    color="tertiary"
                    block="true"
                    size="default"
                    append-icon="mdi-content-cut"
                    disabled
                >
                Cut
                </v-btn>
            </v-col>
        </v-row>
</v-app-bar>
</template>
