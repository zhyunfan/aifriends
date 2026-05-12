<script setup lang="js">
import {ref} from "vue";
import {useUserStore} from "@/stores/user.js";
import api from "@/js/http/api.js";
import {useRouter} from "vue-router";

const username=ref('')
const password=ref('')
const errorMessage=ref('')
//vue中user只能在外面定义
const user=useUserStore()
//useRouter是跳转，useRoute是获取当前url的信息
const router=useRouter()
async function handleLogin(){
  // console.log('登录')
  errorMessage.value=''
  if(!username.value.trim()){
    errorMessage.value='用户名不能为空'
  }else if(!password.value.trim()){
    errorMessage.value='密码不能为空'
  }else{
    try{
      const res=await api.post('api/user/account/login/',{
        username:username.value,
        password:password.value,
      })
      //res是backend/web/views/user/account/login.py中的response
      const data=res.data
      if(data.result==='success'){
        user.setAccessToken(data.access)
        user.setUserInfo(data)
        //跳转
        await router.push({
          name: 'homepage-index'
        })
      }else{
        errorMessage.value=data.result
      }
    }catch (err) {
      console.log(err)
    }
  }
}
</script>

<template>
<!--  mt:margin top-->
  <div class="flex justify-center mt-30">
    <!--将fieldset改为form表单，绑定提交事件，那么回车也会触发该函数,同时需要.prevent阻止默认行为：回车后会刷新页面-->
    <form @submit.prevent="handleLogin" class="fieldset bg-base-200 border-base-300 rounded-box w-xs border p-4">
      <label class="label">用户名</label>
      <input v-model="username" type="text" class="input" placeholder="用户名" />

      <label class="label">密码</label>
      <input v-model="password" type="password" class="input" placeholder="密码" />
      <p v-if="errorMessage" class="text-sm text-red-500 mt-1" >{{errorMessage}}</p>
      <button class="btn btn-neutral mt-4">登录</button>
      <div class="flex justify-end">
        <RouterLink :to="{name:'user-account-register-index'}" class="btn btn-sm btn-ghost text-gray-500">
          注册
        </RouterLink>
      </div>
    </form>
  </div>

</template>

<style scoped>

</style>