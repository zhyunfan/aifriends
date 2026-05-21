<script setup lang="js">

import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
import {ref, useTemplateRef} from "vue";
import streamApi from "@/js/http/streamApi.js";


const props=defineProps(['friendId'])
const inputRef=useTemplateRef('input-ref')
const message=ref('')// 响应式数据
// 避免用户连续发消息
let isProcessing=false

function focus(){
  inputRef.value.focus()
}
async function handleSend(){
  if(isProcessing)return
  isProcessing=true
  const content=message.value.trim()
  if(!content)return
  message.value=''

  try{
    await streamApi('/api/friend/message/chat',{
      body:{
        friend_id:props.friendId,
        message:content,
      },
      // 用来接收消息
      onmessage(data,isDone){
        if(isDone){
          isProcessing=false
        }else if(data.content){
          console.log(data.content)
        }
      },
      // 用来接收错误
      onerror(){
        isProcessing=false
      },
    })
  }catch (err){
    console.log(err)
    isProcessing=false
  }


  /*
  http请求不适用了
  try{
    const res=await api.post('api/friend/message/chat',{
      friend_id:props.friendId,
      message:content,
    })
    console.log(res.data.result)
  }catch (err){
    console.log(err)
  }*/
}
defineExpose({
  focus,
})
</script>

<template>
<!--  发送和语音两个组件都是垂直居中-->
  <form @submit.prevent="handleSend" class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
    <!--当 message 的值改变时，输入框的显示内容会自动更新,
    当用户在输入框中输入内容时，message 的值会自动同步更新-->
    <input
        ref="input-ref"
        v-model="message"
        class="input bg-black/30 backdrop-blur-sm text-white text-base w-full h-full  rounded-2xl pr-20"
        type="text"
        placeholder="文本输入..."
    >
    <!--    div方块是居中的，但是里面的组件没有居中，因此div也需要设置居中-->
    <div @click="handleSend" class="absolute right-2 w-8 h-8 flex justify-center items-center cursor-pointer">
      <SendIcon></SendIcon>
    </div>
    <div class="absolute right-10 w-8 h-8 flex justify-center items-center cursor-pointer">
      <MicIcon></MicIcon>
    </div>
  </form>
</template>

<style scoped>

</style>