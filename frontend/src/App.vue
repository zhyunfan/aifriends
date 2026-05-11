<script setup lang="js">
// js
import NavBar from "@/components/navbar/NavBar.vue";
import {onMounted} from "vue";
import {useUserStore} from "@/stores/user.js";
import api from "@/js/http/api.js";
import {useRoute, useRouter} from "vue-router";
const user=useUserStore()
// router：是“路由器”，负责管理路由规则、控制跳转。
// route：是“当前路由信息”，是一个只读的对象，描述当前页面的状态。
const route=useRoute()
const router=useRouter()
onMounted(async()=>{
  try{
    const res=await api.get('api/user/account/get_user_info/')
    const data=res.data
    if(data.result==='success'){
      user.setUserInfo(data)
    }
  }catch(err){
    console.log(err)
  }finally {
    user.setHasPulledUserInfo(true)
    //判断是否需要登录
    if(route.meta.needLogin&&!user.isLogin()){
      //用replace:网页不能后退“⬅”，用push可以后退
      await router.replace({
        name: 'user-account-login-index',
      })
    }
  }
})
</script>

<template>
  <!--html-->
  <!--<NavBar>页面内容</NavBar>-->
  <NavBar>
    <!--显示当前路由匹配到的页面组件
    即会自动根据url域名后面的内容去router/index.ts中找该内容对应的组件，然后将该组件渲染到RouterView位置-->
    <RouterView></RouterView>
  </NavBar>
</template>

<style scoped>
/*css*/
</style>
