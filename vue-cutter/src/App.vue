<script setup>
import { useTheme } from 'vuetify';

const theme = useTheme();

import MenuBar from './components/MenuBar.vue';
import SideBar from './components/SideBar.vue';
import CutterBar from './components/CutterBar.vue';
import MainArea from './components/MainArea.vue';
import FooterArea from './components/FooterArea.vue';

</script>

<template>
  <v-app>
      <MenuBar />
      <SideBar />
      <CutterBar />
      <v-main>
        <v-container
          class="pa-2"
          fluid
          elevation="5"
        >
          <MainArea />
        </v-container>
      </v-main>
      <FooterArea />
  </v-app>
</template>

