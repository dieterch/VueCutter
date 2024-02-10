<script setup>

import MenuBar from './components/MenuBar.vue';
import SideBar from './components/SideBar.vue';
import CutterBar from './components/CutterBar.vue';
import MainArea from './components/MainArea.vue';
import FooterArea from './components/FooterArea.vue';
import { useTheme } from 'vuetify'
import { get_themecookie } from '@/app';

const theme = useTheme()
theme.global.name.value = get_themecookie()
</script>

<template>
  <v-app>
      <MenuBar />
      <SideBar />
      <CutterBar />
      <v-main
        color="black"
      >
        <v-container
          class="pa-0"
          fluid
          elevation="0"
        >
          <MainArea />
        </v-container>
      </v-main>
      <FooterArea />
  </v-app>
</template>
