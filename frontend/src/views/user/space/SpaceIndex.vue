<script setup lang="ts">
import {useRoute, useRouter} from "vue-router";
// 取当前url的信息
const route=useRoute()
// 打开一个新页面或后退
const router=useRouter()
//e.g.打开一个新页面：自动跳到首页
// router.push({
//   name:'homepage-index'
// })
</script>

<template>
<!--  route.params：参数列表 user_id:参数名(router/index.ts中设置的path:'/user/space/:user_id/')-->
个人空间：{{ route.params.user_id }}
</template>

<style scoped>

</style>