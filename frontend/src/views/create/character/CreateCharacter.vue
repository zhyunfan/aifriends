<script setup lang="js">

import Photo from "@/views/create/character/components/Photo.vue";
import Name from "@/views/create/character/components/Name.vue";
import Profile from "@/views/create/character/components/Profile.vue";
import BackgroundImage from "@/views/create/character/components/BackgroundImage.vue";
import {useUserStore} from "@/stores/user";
import {ref, useTemplateRef} from "vue";
import {base64ToFile} from "@/js/utils/base64_to_file.js";
import api from "@/js/http/api.js";
import {useRouter} from "vue-router";
const user=useUserStore()
const router=useRouter()
const photoRef=useTemplateRef('photo-ref')
const nameRef=useTemplateRef('name-ref')
const profileRef=useTemplateRef('profile-ref')
const backgroundImageRef=useTemplateRef('background-image-ref')
const errorMessage=ref('')
async function handleCreate(){
  const photo=photoRef.value.myPhoto
  //如果不加?刚开始点击创建会报错，说myName为空，因为我们没有给Name.vue组件传递name属性即没有在父组件即本文件里面设置:name=...
  const name=nameRef.value.myName?.trim()
  const profile=profileRef.value.myProfile?.trim()
  const backgroundImage=backgroundImageRef.value.myBackgroundImage
  errorMessage.value=''
  if(!photo){
    errorMessage.value='头像不能为空'
  }else if(!name){
    errorMessage.value='名字不能为空'
  }else if(!profile){
    errorMessage.value='角色介绍不能为空'
  }else if(!backgroundImage){
    errorMessage.value='聊天背景不能为空'
  }else{
    const formData=new FormData()
    // 参数键不能随便取名，由create.py得到
    formData.append('name',name)
    formData.append('profile',profile)
    formData.append('photo',base64ToFile(photo,'photo.png'))
    formData.append('background_image',base64ToFile(backgroundImage,'background_image.png'))
    try{
      const res=await api.post('api/create/character/create/',formData)
      const data=res.data
      if(data.result==='success'){
        await router.push({
          name:'user-space-index',
          params:{
            user_id:user.id,
          }
        })
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
      <div class="card-body">
        <h3 class="text-lg font-bold my-4">创建角色</h3>
        <Photo ref="photo-ref"></Photo>
        <Name ref="name-ref"></Name>
        <Profile ref="profile-ref"></Profile>
        <BackgroundImage ref="background-image-ref"></BackgroundImage>
        <p v-if="errorMessage" class="text-sm text-red-500">{{errorMessage}}</p>
        <div class="flex justify-center">
          <button @click="handleCreate" class="btn btn-neutral w-60 mt-2">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>











