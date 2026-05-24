<script setup lang="js">
import {computed, nextTick, ref, useTemplateRef} from "vue";
import InputField from "@/components/character/chat_field/input_field/InputField.vue";
import CharacterPhotoField from "@/components/character/chat_field/character_photo_field/CharacterPhotoField.vue";
import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
import ChatHistory from "@/components/character/chat_field/chat_history/ChatHistory.vue";

const props=defineProps(['friend'])
const modalRef=useTemplateRef('modal-ref')
const inputRef=useTemplateRef('input-ref')
const history=ref([])
const chatHistoryRef=useTemplateRef('chat-history-ref')

async function showModal(){
  modalRef.value.showModal()
  await nextTick()
  // 实现自动聚焦输入框
  inputRef.value.focus()
}
// 将角色的模态框背景图片设置成聊天背景：
// computed 就像一个自动缓存的计算结果。当它依赖的数据发生变化时，它会自动重新计算；如果依赖的数据没变，它会直接返回上次缓存的结果，不会重复执行,响应式：依赖的数据变化时，自动更新
const modalStyle = computed(() => {
  if (props.friend) {//刚开始是空的
    return {
      backgroundImage: `url(${props.friend.character.background_image})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
    }
  } else {
    return {}
  }
})
//添加一条消息
function handlePushBackMessage(msg){
  history.value.push(msg)
  chatHistoryRef.value.scrollToBottom()
}
//在最后一条消息上补充内容
function handleAddToLastMessage(delta){
  history.value.at(-1).content+=delta
  chatHistoryRef.value.scrollToBottom()
}
function handlePushFrontMessage(msg){
    //往后加是push,往前加是unshift
    history.value.unshift(msg)
}
function handleClose(){
  modalRef.value.close()
  inputRef.value.close()
}
defineExpose({
  showModal
})
</script>

<template>
  <!--模态框里面定义了relative-->
  <dialog ref="modal-ref" class="modal">
<!--    :style="modalStyle"：Vue 的动态样式绑定
:style 是 v-bind:style 的简写-->
    <div class="modal-box w-90 h-150" :style="modalStyle">
      <button @click="handleClose" class="btn btn-sm btn-circle btn-ghost bg-transparent absolute right-1 top-1">✕</button>
      <ChatHistory
        ref="chat-history-ref"
        v-if="friend"
        :history="history"
        :friendId="friend.id"
        :character="friend.character"
        @pushFrontMessage="handlePushFrontMessage"
      ></ChatHistory>
      <InputField
          v-if="friend"
          ref="input-ref"
          :friendId="friend.id"
          @pushBackMessage="handlePushBackMessage"
          @addToLastMessage="handleAddToLastMessage"
      ></InputField>
      <CharacterPhotoField v-if="friend" :character="friend.character"></CharacterPhotoField>
    </div>
  </dialog>
</template>

<style scoped>

</style>





