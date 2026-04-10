<script setup lang="ts">
// js
import NavBar from "@/components/navbar/NavBar.vue";
</script>

<template>
  <!--html-->
  <!--<NavBar>页面内容</NavBar>-->
  <NavBar>
    <!--显示当前路由匹配到的页面组件
    即会自动根据url域名后面的内容去router/index.ts中找该内容对应的组件，然后将该组件渲染到RouterView位置-->
    <RouterView></RouterView>
  </NavBar>
</template>

<style scoped>
/*css*/
</style>
