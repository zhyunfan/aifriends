<script setup lang="js">

import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
</script>

<template>
<!--  发送和语音两个组件都是垂直居中-->
  <div class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
    <input
      class="input bg-black/30 backdrop-blur-sm text-white text-base w-full h-full  rounded-2xl pr-20"
      type="text"
      placeholder="文本输入..."
    >
<!--    div方块是居中的，但是里面的组件没有居中，因此div也需要设置居中-->
    <div class="absolute right-2 w-8 h-8 flex justify-center items-center cursor-pointer">
      <SendIcon></SendIcon>
    </div>
    <div class="absolute right-10 w-8 h-8 flex justify-center items-center cursor-pointer">
      <MicIcon></MicIcon>
    </div>
  </div>
</template>

<style scoped>

</style>