<script setup lang="js">
import {ref} from "vue";
import UpdateIcon from "@/components/character/icons/UpdateIcon.vue";
import {useUserStore} from "@/stores/user.js";
import RemoveIcon from "@/components/character/icons/RemoveIcon.vue";
import api from "@/js/http/api.js";

const props=defineProps(['character','canEdit'])
const emit=defineEmits(['remove'])
const isHover=ref(false)
const user=useUserStore()
async function handleRemoveCharacter(){
  try{
    const res=await api.post('api/create/character/remove/',{
      character_id:props.character.id,
    })
    if(res.data.result==='success'){
      // 子组件向父组件发送一个名为 remove 的事件，并携带当前角色的 id 作为参数
      // 父组件执行 @remove 绑定的方法 handleRemoveCharacter
      // 参数 props.character.id 作为 handleRemoveCharacter 的第一个参数传入
      // 子组件不自己删除数据是因为数据是从父组件传到子组件
      emit('remove',props.character.id)
    }
  }catch (err){
    console.log(err)
  }
}
</script>

<template>
  <div>
    <div class="avatar cursor-pointer" @mouseover="isHover=true" @mouseout="isHover=false">
      <div class="w-60 h-100 rounded-2xl relative">
        <!-- 在 <template> 中访问 props，不需要加 props.在 <script> 中访问 props 的值，必须加 props. -->
        <img :src="character.background_image" class="transition-transform duration-300" :class="{'scale-120':isHover}" alt="">
        <div class="absolute left-0 top-50 w-60 h-50 bg-linear-to-t from-white/40 to-transparent"></div>
        <div v-if="canEdit&&character.author.user_id===user.id" class="absolute right-0 top-50">
          <RouterLink :to="{name:'update-character',params:{character_id:character.id}}" class="btn btn-circle btn-ghost bg-transparent">
            <UpdateIcon></UpdateIcon>
          </RouterLink>
          <button @click="handleRemoveCharacter" class="btn btn-circle btn-ghost bg-transparent">
            <RemoveIcon></RemoveIcon>
          </button>
        </div>
        <div class="absolute left-4 top-54 avatar">
          <div class="w-16 rounded-full ring-3 ring-white">
            <img :src="character.photo" alt="">
          </div>
        </div>
        <div class="absolute left-24 top-58 right-4text-white font-bold line-clamp-1 break-all">
          {{character.name}}
        </div>
        <div class="absolute left-4 top-72 right-4text-white line-clamp-4 break-all">
          {{character.profile}}
        </div>
      </div>
    </div>
    <RouterLink :to="{name:'user-space-index',params:{user_id:character.author.user_id}}" class="flex items-center mt-4 gap-2 w-60">
      <!--主轴方向 决定排列方向，所以flex表示组件水平排列，items-center子元素垂直居中-->
      <div class="avatar">
        <div class="w-7 rounded-full">
          <img :src="character.author.photo" alt="">
        </div>
      </div>
      <div class="text-sm line-clamp-1 break-all">{{character.author.username}}</div>
    </RouterLink>
  </div>
</template>

<style scoped>

</style>














