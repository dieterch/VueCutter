<script setup>
import { ref, computed } from 'vue'
import axios from 'axios';
import {
    host, protocol,
    inplace, useffmpeg, lmovie, movie, section,
    t0, t1, lmovie_cut_info,
    cutterdialog, cutterdialog_enable_cut, 
    reset_cutlist, cutlist, cutmsg, progress_status
} from '@/app';

async function do_cut() {
    const endpoint = `${protocol.value}//${host.value}/cut2`
    try {
        const response = await axios.post(endpoint,
        {   
            "section": section.value, 
            "movie_name": lmovie.value,
            "cutlist": cutlist.value,
            "inplace": inplace.value,
            "useffmpeg": useffmpeg.value,
            "etaest": lmovie_cut_info.value.eta
        },
        { headers: { 'Content-type': 'application/json',}});
        console.log(response.data)
        progress()
        cutterdialog.value = false
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
    }, 3000)
    console.log("progress", timer_id)
}
</script>

<template>
    <v-dialog
    v-model="cutterdialog"
    persistent="true"
    width="auto"
    >
        <v-card
            title="Cut Dialog"
            color="dialogbackground"
            :subtitle="movie"
        >
            <v-card-text>
                <v-table 
                    density="compact"
                    theme="dark"        
                    >
                    <thead>
                        <tr>
                            <th class="text-left">Name</th>
                            <th class="text-left">Wert</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr
                            v-for = "(val, key) in cutmsg"
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
                <v-row nogap>
                    <v-col cols="4">
                        <v-btn
                            class="ma-0 ml-4"
                            color="danger-button"
                            variant="flat"
                            prepend-icon="mdi-content-cut"
                            width="120px"
                            @click="do_cut"
                            :disabled="!cutterdialog_enable_cut"
                            >
                            Cut
                        </v-btn>
                    </v-col>
                    <v-col cols="4">
                        <v-btn
                            class="ma-0"
                            color="primary-button"
                            variant="flat"
                            prepend-icon="mdi-cancel"
                            width="120px"
                            @click="cutterdialog = false"
                            >
                            Cancel
                        </v-btn>
                    </v-col>
                    <v-col cols="4">
                        <v-btn
                            class="ma-0"
                            color="tertiary-button"
                            variant="flat"
                            prepend-icon="mdi-restart"
                            width="120px"
                            @click="reset_cutlist"
                            >
                            Reset
                        </v-btn>
                    </v-col>
                    <v-spacer/>
                    <!--/v-row>
                        <v-row-->
                    <v-col 
                        cols="3"
                        class="ma-0 ml-3 pa-0"
                        >
                        <v-checkbox
                        density="compact"
                        class="mt-0 ml-3"
                        v-model="useffmpeg"
                        label="FFMP"
                        ></v-checkbox>
                    </v-col>
                    <v-col 
                        cols="3"
                        class="ma-0 ml-11 pa-0"
                        >
                        <v-checkbox
                        density="compact"
                        class="mt-0"
                        v-model="inplace"
                        label="Inplace"
                        ></v-checkbox>
                    </v-col>
                    <v-spacer/>
                </v-row>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>