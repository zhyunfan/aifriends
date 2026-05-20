<script setup lang="js">
import {computed, useTemplateRef} from "vue";
import InputField from "@/components/character/chat_field/input_field/InputField.vue";
import CharacterPhotoField from "@/components/character/chat_field/character_photo_field/CharacterPhotoField.vue";
import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";

const props=defineProps(['friend'])
const modalRef=useTemplateRef('modal-ref')
function showModal(){
  modalRef.value.showModal()
}
// 将角色的模态框背景图片设置成聊天背景：
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
defineExpose({
  showModal
})
</script>

<template>
  <!--模态框-->
  <dialog ref="modal-ref" class="modal">
<!--    :style="modalStyle"：Vue 的动态样式绑定
:style 是 v-bind:style 的简写-->
    <div class="modal-box w-90 h-150" :style="modalStyle">
      <button @click="modalRef.close()" class="btn btn-sm btn-circle btn-ghost bg-transparent absolute right-1 top-1">✕</button>
      <InputField></InputField>
      <CharacterPhotoField v-if="friend" :character="friend.character"></CharacterPhotoField>
    </div>
  </dialog>
</template>

<style scoped>

</style>