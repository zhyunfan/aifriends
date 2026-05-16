<script setup lang="js">
/*import {useRoute, useRouter} from "vue-router";
import UserInfoField from "@/views/user/space/components/UserInfoField.vue";
// 取当前url的信息
const route=useRoute()
// 打开一个新页面或后退
const router=useRouter()
//e.g.打开一个新页面：自动跳到首页
// router.push({
//   name:'homepage-index'
// })*/
import UserInfoField from "@/views/user/space/components/UserInfoField.vue";
import {nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef} from "vue";
import api from "@/js/http/api";
import {useRoute} from "vue-router";

const userProfile=ref(null)
const characters=ref([])
// 如果正在加载就不要重复发请求了
const isLoading=ref(false)
// 云端是否还有角色
const hasCharacters=ref(true)
const route=useRoute()
const sentinelRef=useTemplateRef('sentinel-ref')
function checkSentinelVisible() {  // 判断哨兵是否能被看到
  if (!sentinelRef.value) return false

  const rect = sentinelRef.value.getBoundingClientRect()
  return rect.top < window.innerHeight && rect.bottom > 0
}
async function loadMore(){
  console.log('11111111111111111111111111111111111')
  // 如果正在加载中或者没有角色了
  if(isLoading.value||!hasCharacters.value)return
  isLoading.value=true
  //从云端加载的角色
  let newCharacters=[]
  try{
    const res=await api.get('api/create/character/get_list/',{
      params:{
        items_count:characters.value.length,
        user_id:route.params.user_id,
      }
    })
    const data=res.data
    if(data.result==='success'){
      console.log('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
      userProfile.value=data.user_profile
      console.log(userProfile.value.username)
      console.log(userProfile.value.photo)
      newCharacters=data.characters
    }
  }catch(err){
    console.log(err)
  }finally {
    isLoading.value=false
    if(newCharacters.length===0){
      hasCharacters.value=false
    }else{
      characters.value.push(...newCharacters)
      // 等待元素全部渲染完成
      await nextTick()
      // 渲染完后看哨兵能否被看到
      if(checkSentinelVisible()){
        await loadMore()
      }
    }
  }
}

// 监听器
let observer=null
//元素被挂载时
onMounted(async ()=>{
  await loadMore()
  // 交叉观察器:一个持续检测"元素与视口重叠程度"的工具
  // 区域A：目标元素（你要监听的DOM元素）
  // 区域B：浏览器视口（用户能看到的窗口区域）
  // 当这两个区域发生交叉（即元素进入或离开视线范围）时，就会触发回调。
  observer=new IntersectionObserver(
    entries => {
      entries.forEach(entry=>{
        if(entry.isIntersecting){
          // console.log('红色出现了')
          loadMore()
        }
      })
    }, {root:null,rootMargin:'2px',threshold:0}
  )
  observer.observe(sentinelRef.value)
})
// 释放资源
onBeforeUnmount(()=>{
  observer?.disconnect()
})
</script>

<template>
  <!--route.params：参数列表 user_id:参数名(router/index.ts中设置的path:'/user/space/:user_id/')
      个人空间：{{ route.params.user_id }}-->

  <!--mb:margin-bottom上半部分用户信息区域，下半部分角色列表-->
  <div class="flex flex-col items-center mb-12">
    <UserInfoField v-if="userProfile" :userProfile="userProfile"></UserInfoField>
    <div class="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-9 mt-12 justify-items-center w-full px-9">

    </div>
    <!--哨兵 在加载卡片时会加到哨兵前面，如果页面看不到哨兵就停止加载卡片，向下滚动页面时如果看到哨兵就继续加载-->
    <div ref="sentinel-ref" class="h-2 mt-800 w-100 bg-red-500"></div>
    <div v-if="isLoading" class="text-gray-500 mt-4">加载中...</div>
    <div v-else-if="!hasCharacters" class="text-gray-500 mt-4">没有更多角色了</div>
  </div>
</template>

<style scoped>

</style>












