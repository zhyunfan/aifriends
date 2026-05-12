<script setup lang="js">
import {useUserStore}from "@/stores/user"
import UserSpaceIndex from "@/components/navbar/icons/UserSpaceIndex.vue";
import UserLogoutIcon from "@/components/navbar/icons/UserLogoutIcon.vue";
import UserProfileIcon from "@/components/navbar/icons/UserProfileIcon.vue";
import api from "@/js/http/api.js";
import {useRouter} from "vue-router";

// user = Pinia 管理的用户状态仓库实例
// 它是一个响应式对象包含状态（如 user.token）、getters（如 user.userName）、actions（如 user.login()）在 Vue 组件中使用时会自动追踪依赖
// 在任何组件中调用 useUserStore() 得到的是同一个实例（单例模式）
// 修改 user 中的状态会自动更新所有使用它的组件,持久化
// 简单说：user 就是你在前端应用中管理用户登录状态、用户信息的"中央仓库"。
const user=useUserStore()

function closeMenu() {
  const element = document.activeElement
  if (element && element instanceof HTMLElement) element.blur()
 }
const router=useRouter()
async function handleLogout(){
  try{
    const res=await api.post('api/user/account/logout/')
    if(res.data.result==='success'){
      user.logout()
      await router.push({
        name: 'homepage-index'
      })
    }
  }catch(err){
    console.log(err)
  }
}
</script>

<template>
  <div class="dropdown dropdown-end">
    <div tabindex="0" role="button" class="avatar btn btn-circle w-8 h-8 mr-6">
      <div class="w-8 rounded-full">
        <img :src="user.photo">
      </div>
    </div>
    <ul tabindex="-1" class="dropdown-content menu bg-base-100 rounded-box z-1 w-48 p-2 shadow-lg">
      <li>
        <!--user-space-index:index.js中的，user_id是index.js中的path:'/user/space/:user_id/'中的，user.id是user.js中返回的id-->
        <RouterLink @click="closeMenu" :to="{name:'user-space-index',params:{user_id:user.id}}">
          <div class="avatar">
            <div class="w-10 rounded-full">
              <img :src="user.photo">
            </div>
          </div>
          <!--line-clamp-1最多1行，超过的变成省略号
          break-all表示可以让单词在容易位置换行即只要超过行宽就会换行-->
          <span class="text-base font-bold line-clamp-1 break-all">{{user.username}}</span>
        </RouterLink>
      </li>
      <li>
        <RouterLink @click="closeMenu" :to="{name:'user-space-index',params:{user_id:user.id}}"class="text-sm font-bold py-3">
          <UserSpaceIndex>
          </UserSpaceIndex>
          个人空间
        </RouterLink>
      </li>
      <li>
        <RouterLink @click="closeMenu" :to="{name:'user-profile-index'}" class="text-sm font-bold py-3">
          <UserProfileIcon>
          </UserProfileIcon>
          编辑资料
        </RouterLink>
      </li>
      <li></li>
      <li>
        <a @click="handleLogout" class="text-sm font-bold py-3">
          <UserLogoutIcon>
          </UserLogoutIcon>
          退出登录
        </a>
      </li>
    </ul>
  </div>
</template>

<style scoped>

</style>









