<script setup lang="ts">
import {ref, watch} from "vue";

const props=defineProps(['profile'])
// 需要用到响应式，因为裁剪图片那么myPhoto会变
const myProfile=ref(props.profile)
watch(()=>props.profile,newVal=>{
  myProfile.value=newVal
})
defineExpose({
  myProfile,
})
</script>

<template>
  <fieldset class="fieldset">
    <label class="label text-base">简介</label>
    <textarea v-model="myProfile" rows="6" class="textarea w-108"></textarea>
  </fieldset>
</template>

<style scoped>

</style>