<script setup lang="js">

import Photo from "@/views/create/character/components/Photo.vue";
import Name from "@/views/create/character/components/Name.vue";
import Profile from "@/views/create/character/components/Profile.vue";
import BackgroundImage from "@/views/create/character/components/BackgroundImage.vue";
import {useUserStore} from "@/stores/user";
import {onMounted, ref, useTemplateRef} from "vue";
import {base64ToFile} from "@/js/utils/base64_to_file.js";
import api from "@/js/http/api.js";
import {useRoute, useRouter} from "vue-router";
const user=useUserStore()
const router=useRouter()
//得到当前角色的id
const route=useRoute()
//路由中：path:'/create/character/update/:character_id/',
//由于characterId不用在前端显示，所以不用设置成响应式变量
const characterId=route.params.character_id
//character需要在前端显示
const character=ref(null)
onMounted(async ()=>{
  try{
    const res=await api.get('api/create/character/get_single/',{
      params:{
        //character_id是因为get_single.py中的request.get_param('character_id')
        character_id:characterId,
      }
    })
    const data=res.data
    if (data.result==='success'){
      character.value=data.character
    }
  }catch (err){
    console.log(err)
  }
})


const photoRef=useTemplateRef('photo-ref')
const nameRef=useTemplateRef('name-ref')
const profileRef=useTemplateRef('profile-ref')
const backgroundImageRef=useTemplateRef('background-image-ref')
const errorMessage=ref('')
async function handleUpdate(){
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
    formData.append('character_id',characterId)
    formData.append('name',name)
    formData.append('profile',profile)
    //在js中调用响应式变量时需要加上.value，在html中调用时不需要加.value
    if(photo!==character.value.photo){
      formData.append('photo',base64ToFile(photo,'photo.png'))
    }
    if(backgroundImage!==character.value.background_image){
      formData.append('background_image',base64ToFile(backgroundImage,'background_image.png'))
    }
    try{
      const res=await api.post('api/create/character/update/',formData)
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
  <div v-if="character" class="flex justify-center">
    <div class="card w-120 bg-base-200 shadow-sm mt-16">
      <div class="card-body">
        <h3 class="text-lg font-bold my-4">更新角色</h3>
        <Photo ref="photo-ref" :photo="character.photo"></Photo>
        <Name ref="name-ref" :name="character.name"></Name>
        <Profile ref="profile-ref" :profile="character.profile"></Profile>
        <BackgroundImage ref="background-image-ref" :backgroundImage="character.background_image"></BackgroundImage>
        <p v-if="errorMessage" class="text-sm text-red-500">{{errorMessage}}</p>
        <div class="flex justify-center">
          <button @click="handleUpdate" class="btn btn-neutral w-60 mt-2">更新</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>











