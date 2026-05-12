<script setup lang="js">

import Photo from "@/views/user/profile/components/Photo.vue";
import Username from "@/views/user/profile/components/Username.vue";
import Profile from "@/views/user/profile/components/Profile.vue";
import {useUserStore} from "@/stores/user";
import {ref, useTemplateRef} from "vue";
import {base64ToFile} from "@/js/utils/base64_to_file.js";
import api from "@/js/http/api.js";
const user=useUserStore()
const photoRef=useTemplateRef('photo-ref')
const usernameRef=useTemplateRef('username-ref')
const profileRef=useTemplateRef('profile-ref')
const errorMessage=ref('')

async function handleUpdate(){
  const photo=photoRef.value.myPhoto
  const username=usernameRef.value.myUsername.trim()
  const profile=profileRef.value.myProfile.trim()
  errorMessage.value=''

  if(!photo){
    errorMessage.value='头像不能为空'
  }else if(!username){
    errorMessage.value='用户名不能为空'
  }else if(!profile){
    errorMessage.value='简介不能为空'
  }else{
    // 创建一个表单数据对象，用于构造一组键值对，方便通过 AJAX (例如 fetch 或 axios) 发送给服务器。
    const formData=new FormData()
    formData.append('username',username)
    formData.append('profile',profile)
    if(photo!==user.photo){
      formData.append('photo',base64ToFile(photo,'photo.png'))
    }
    try{
      const res=await api.post('api/user/profile/update/',formData)
      const data=res.data
      if(data.result==='success'){
        user.setUserInfo(data)
      }else{
        errorMessage.value=data.result
      }
    }catch(err){
      console.log(err)
    }
  }
}
</script>

<template>
  <div class="flex justify-center">
    <div class="card w-120 bg-base-200 shadow-sm mt-16">
      <div class="card-body ">
        <h3 class="text-lg font-bold my-4">编辑资料</h3>
        <!--没有冒号：子组件收到的值：字符串 "user.photo"（原封不动的文本）
            有冒号：子组件收到的值：变量 user.photo 里面存的实际内容（比如一个图片网址 "https://example.com/avatar.jpg"）-->
        <Photo ref="photo-ref" :photo="user.photo"></Photo>
        <Username ref="username-ref" :username="user.username"></Username>
        <Profile ref="profile-ref" :profile="user.profile"></Profile>
        <p v-if="errorMessage" class="text-sm text-red-500">{{errorMessage}}</p>
        <div class="flex justify-center">
          <!--这里不像LoginIndex.vue一样将函数绑定到表单是因为在编辑profile时可以回车吧-->
          <button @click="handleUpdate" class="btn btn-neutral w-60 mt-2">更新</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>