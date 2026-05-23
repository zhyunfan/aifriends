<script setup lang="js">
  import Message from "@/components/character/chat_field/chat_history/message/Message.vue";
  import {nextTick, onBeforeUnmount, onMounted, useTemplateRef} from "vue";
  import api from "@/js/http/api.js";

  const props=defineProps(['history','friendId','character'])
  const emit=defineEmits(['handlePushFrontMessage'])
  const scrollRef=useTemplateRef('scroll-ref')
  const sentinelRef=useTemplateRef('sentinel-ref')//哨兵
  //不用加载到页面布局里所以不用响应式变量
  let isLoading=false
  let hasMessages=true
  let lastMessageId=0

  function checkSentinelVisible() {  // 判断哨兵是否能被看到
    if (!sentinelRef.value) return false

    const sentinelRect = sentinelRef.value.getBoundingClientRect()
    const scrollRect = scrollRef.value.getBoundingClientRect()
    return sentinelRect.top < scrollRect.bottom && sentinelRect.bottom > scrollRect.top
  }

  async function loadMore(){
    if(isLoading||!hasMessages)return
    isLoading=true
    let newMessages=[]
    try{
      const res=await api.get('/api/friend/message/get_history',{
        params:{
          last_message_id:lastMessageId,
          friend_id:props.friendId,
        }
      })
      const data=res.data
      if(data.result==='success'){
        newMessages=data.messages
      }
    }catch (err){
      console.log(err)
    }finally {
      isLoading=false
      if(newMessages.length===0){
        hasMessages=false
      }else{
        const oldHeight=scrollRef.value.scrollHeight
        const oldTop=scrollRef.value.scrollTop
        //of是输出内容，in输出下标
        for(const m of newMessages){
          //往上滑时先加载的是ai,后加载我们问题
          emit('pushFrontMessage',{
            role:'ai',
            content:m.output,
            id:crypto.randomUUID(),
          })
          emit('pushFrontMessage',{
            role:'user',
            content:m.user_message,
            id:crypto.randomUUID(),
          })
          //最后一个更新的就是最后一个id
          lastMessageId=m.id
        }
        await nextTick()
        const newHeight=scrollRef.value.scrollHeight
        scrollRef.value.scrollTop=oldTop+newHeight-oldHeight
        if(checkSentinelVisible()){
          await loadMore()
        }
      }
    }
  }
  let observer=null
  onMounted(async ()=>{
    await loadMore()
    observer=new IntersectionObserver(entries => {
      entries.forEach(entry=>{
        if(entry.isIntersecting){
          loadMore()
        }
      })
    },
        {root:null,rootMargin:'2px',threshold:0}
    )
    observer.observe(sentinelRef.value)
  })
  onBeforeUnmount(()=>{
    observer?.disconnect()
  })
  async function scrollToBottom(){
    await nextTick()
    // 浏览器有自动保护机制，会自动将窗口往上到页面内容的底部
    // 适用于任何拥有滚动条的 原生 HTML 元素
    scrollRef.value.scrollTop=scrollRef.value.scrollHeight
  }

  defineExpose({
    scrollToBottom
  })
</script>

<template>
  <!-- overflow-y-scroll溢出纵向滚动 -->
  <div ref="scroll-ref" class="absolute top-18 left-0 w-90 h-112 overflow-y-scroll no-scrollbar">
    <div ref="sentinel-ref" class="h-2"></div>
    <!-- v-for用于列表渲染的指令，可以根据数组或对象循环生成多个元素/组件Message。
          :message="message"：将当前循环的消息对象作为 prop 传递给 Message 组件
          :character="character"：传递一个固定值（不随循环变化）,这里因为要渲染角色头像-->
    <Message
      v-for="message in history"
      :key="message.id"
      :message="message"
      :character="character"></Message>
  </div>
</template>

<style scoped>
/*Webkit 内核浏览器（Chrome、Safari、Opera、Edge 新版）
隐藏 Chrome, Safari 和 Opera 的滚动条
::-webkit-scrollbar 是 Webkit 浏览器的伪元素，用于自定义滚动条样式*/
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
/* 隐藏 IE, Edge 和 Firefox 的滚动条 */
.no-scrollbar {
  -ms-overflow-style: none; /* IE and Edge 隐藏滚动条*/
  scrollbar-width: none; /* Firefox 将滚动条宽度设为 0（隐藏）*/
}
</style>