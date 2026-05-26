<script setup lang="js">

import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
import {onUnmounted, ref, useTemplateRef} from "vue";
import streamApi from "@/js/http/streamApi.js";
import Microphone from "@/components/character/chat_field/input_field/Microphone.vue";


const props=defineProps(['friendId'])
const emit=defineEmits(['pushBackMessage','addToLastMessage'])
const inputRef=useTemplateRef('input-ref')
const message=ref('')// 响应式数据
let processId=0
const showMic=ref(false)//是否显示麦克风组件

let mediaSource = null;
let sourceBuffer = null;
let audioPlayer = new Audio(); // 全局播放器实例
let audioQueue = [];           // 待写入 Buffer 的二进制队列
let isUpdating = false;        // Buffer 是否正在写入

//创建一段音频,基于 Media Source Extensions (MSE) 的流式音频播放器初始化函数。它实现了边接收音频数据边播放的功能
const initAudioStream = () => {
    audioPlayer.pause();// 停止当前播放
    audioQueue = [];
    isUpdating = false;

    mediaSource = new MediaSource();// 创建媒体资源容器,是一个特殊的媒体流容器，可以动态往里添加数据
    //URL.createObjectURL() 会生成一个临时 URL（如 blob:http://...），Audio 元素通过这个 URL 就可以播放动态添加的数据
    audioPlayer.src = URL.createObjectURL(mediaSource);// 将 MediaSource 绑定到 audio 元素

    mediaSource.addEventListener('sourceopen', () => {
        try {
            // 添加 MP3 格式的缓冲区
            sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg');
            //触发时机：sourceBuffer.appendBuffer() 写入完成后，通知你：上一块数据已经喂给播放器了，可以喂下一块了
            sourceBuffer.addEventListener('updateend', () => {
                isUpdating = false;
                processQueue();
            });
        } catch (e) {
            console.error("MSE AddSourceBuffer Error:", e);
        }
    });

    audioPlayer.play().catch(e => console.error("等待用户交互以播放音频"));
};
//有音频数据就取出来播放，没有就等着，正在播放就排队
//把 audioQueue 队列中缓存的音频数据，一个个取出来交给浏览器的 sourceBuffer 去播放
//sourceBuffer.updating	浏览器自己的标记，表示正在写入数据	浏览器的缓冲区正忙着，不能打断
const processQueue = () => {
    if (isUpdating || audioQueue.length === 0 || !sourceBuffer || sourceBuffer.updating) {
        return;
    }

    isUpdating = true;
    //shift() 会删除队列中的第一个元素并返回它
    const chunk = audioQueue.shift();
    try {
        sourceBuffer.appendBuffer(chunk);// 把音频数据交给浏览器播放
    } catch (e) {
        console.error("SourceBuffer Append Error:", e);
        isUpdating = false;
    }
};

//关闭一段音频
const stopAudio = () => {
    audioPlayer.pause();
    audioQueue = [];
    isUpdating = false;

    if (mediaSource) {
        if (mediaSource.readyState === 'open') {
            try {
                mediaSource.endOfStream();
            } catch (e) {
            }
        }
        mediaSource = null;
    }

    if (audioPlayer.src) {
        URL.revokeObjectURL(audioPlayer.src);
        audioPlayer.src = '';
    }
};

const handleAudioChunk = (base64Data) => {  // 将语音片段添加到播放器队列中
    try {
        const binaryString = atob(base64Data);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        audioQueue.push(bytes);
        processQueue();
    } catch (e) {
        console.error("Base64 Decode Error:", e);
    }
};

onUnmounted(() => {
    audioPlayer.pause();
    audioPlayer.src = '';
});

function focus(){
  inputRef.value.focus()
}
//event 参数会自动有值，不需要你手动传递，Vue 会自动把原生 DOM 事件对象作为第一个参数传给 handleSend
async function handleSend(event,audio_msg){
  let content
  if(audio_msg){
    // audio_msg 是普通参数,可以直接使用
    content=audio_msg.trim()
  }else{
    //ref 对象，需要 .value 访问
    content=message.value.trim()
  }
  if(!content)return

  //初始化一个音频播放器
  initAudioStream()

  const curId=++processId

  message.value=''

  //要用到v-for,需要唯一id,否则出问题所以用uuid
  emit('pushBackMessage',{role:'user',content:content,id:crypto.randomUUID()})
  emit('pushBackMessage',{role:'ai',content:'',id:crypto.randomUUID()})

  try{
    // 用户输入 → InputField.vue 调用 streamApi → streamApi 发送请求到 chat.py
    //                                           ↓
    //                                 chat.py 返回流式数据yield
    //                                           ↓
    //                                 streamApi 内部 onmessage 接收  (fetch-event-source 内部)
    //                                           ↓
    //                                 调用你传入的 onmessage 回调(检查 options.onmessage 是否存在)
    //                                           ↓
    //                                 InputField.vue 中的回调执行
    await streamApi('/api/friend/message/chat',{
      body:{
        friend_id:props.friendId,
        message:content,
      },
      //回调函数就是你写好但不自己调用，而是交给别人去调用的函数。
      // 执行顺序：
      // 1. 调用 streamApi，传入两个回调函数
      // 2. 继续执行后面的代码（如果有）
      // 3. 服务器返回数据时 → streamApi 自动调用 onmessage
      // 4. 网络出错时 → streamApi 自动调用 onerror
      // 用来接收消息
      onmessage(data,isDone){//是定义的 onmessage 回调函数的参数，由 streamApi 函数内部调用时传递进来的，data 和 isDone 只是参数占位符
        //实现打断的功能，processId是全局的，curId是局部的，这里相当于直接结束了handleSend函数,就打断了对话（因为是流式输出）
        if(curId!==processId)return
        if(data.content){
          emit('addToLastMessage',data.content)
        }
        if(data.audio){
          handleAudioChunk(data.audio)
        }
      },
      // 用来接收错误
      onerror(){
      },
    })
  }catch (err){
    console.log(err)
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
function close(){
  ++processId//当关闭聊天窗口时就停止接收消息
  showMic.value=false//当关闭窗口后如果再次点开该窗口，还是文字输入
  stopAudio()
}
function handleStop(){
  ++processId
  stopAudio()
}
defineExpose({
  focus,
  close,
})
</script>

<template>
<!--  发送和语音两个组件都是垂直居中-->
  <form v-if="!showMic" @submit.prevent="handleSend" class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
    <!--当 message 的值改变时，输入框的显示内容会自动更新,
    当用户在输入框中输入内容时，message 的值会自动同步更新
    JS script 中定义变量 message（响应式数据）
    模板中 v-model="message" 去寻找同名的 message 变量
    Vue 把它们连接起来，形成双向绑定-->
    <input
        ref="input-ref"
        v-model="message"
        class="input bg-black/30 backdrop-blur-sm text-white text-base w-full h-full  rounded-2xl pr-20"
        type="text"
        placeholder="文本输入..."
    >
    <!--div方块是居中的，但是里面的组件没有居中，因此div也需要设置居中-->
    <div @click="handleSend" class="absolute right-2 w-8 h-8 flex justify-center items-center cursor-pointer">
      <SendIcon></SendIcon>
    </div>
    <div @click="showMic=true" class="absolute right-10 w-8 h-8 flex justify-center items-center cursor-pointer">
      <MicIcon></MicIcon>
    </div>
  </form>
  <!--说话中的音浪效果-->
  <Microphone
      v-else
      @close="showMic=false"
      @send="handleSend"
      @stop="handleStop"
  ></Microphone>
</template>

<style scoped>

</style>