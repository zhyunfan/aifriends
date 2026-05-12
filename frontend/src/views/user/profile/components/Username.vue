<script setup lang="ts">
import {ref, watch} from "vue";

const props=defineProps(['username'])
// 需要用到响应式，因为裁剪图片那么myPhoto会变
const myUsername=ref(props.username)
watch(()=>props.username,newVal=>{
  myUsername.value=newVal
})
defineExpose({
  myUsername,
})
</script>

<template>
  <fieldset class="fieldset">
    <label class="label text-base">用户名</label>
    <input v-model="myUsername" type="text" class="input w-108">
  </fieldset>
</template>

<style scoped>

</style>