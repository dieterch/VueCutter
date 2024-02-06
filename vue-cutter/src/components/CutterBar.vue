<script setup>
import { ref, computed } from 'vue'

import { 
    t0, t0_valid, 
    t1, t1_valid,
    inplace,
    ltimeline, 
    hpos } from '@/app';

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

</script>

<template>
    <v-app-bar 
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
                    @click="docut2"
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
