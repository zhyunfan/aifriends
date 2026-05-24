<script setup lang="js">
import {useUserStore} from "@/stores/user";

defineProps(['message','character'])
const user=useUserStore()
</script>

<template>
  <div v-if="message.content">
    <div v-if="message.role==='ai'" class="chat chat-start">
      <div class="chat-image avatar">
        <div class="w-10 rounded-full">
          <img :src="character.photo" alt="">
        </div>
      </div>
      <!--break-all英文也要截断-->
      <div class="chat-bubble whitespace-pre-wrap break-all">{{message.content}}</div>
    </div>
    <div v-else class="chat chat-end">
      <div class="chat-image avatar">
        <div class="w-10 rounded-full">
          <img :src="user.photo" alt="">
        </div>
      </div>
      <div class="chat-bubble chat-bubble-success whitespace-break-spaces break-all">{{message.content}}</div>
    </div>
  </div>
</template>

<style scoped>

</style>









