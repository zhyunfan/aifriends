<script setup lang="js">
import {useUserStore}from "@/stores/user"
import UserSpaceIndex from "@/components/navbar/icons/UserSpaceIndex.vue";
import UserLogoutIcon from "@/components/navbar/icons/UserLogoutIcon.vue";
import UserProfileIcon from "@/components/navbar/icons/UserProfileIcon.vue";
const user=useUserStore()

function closeMenu() {
  const element = document.activeElement
  if (element && element instanceof HTMLElement) element.blur()
 }
</script>

<template>
  <div class="dropdown dropdown-end">
    <div tabindex="0" role="button" class="avatar btn btn-circle w-8 h-8 mr-6">
      <div class="w-8 rounded-full">
        <img :src="user.photo">
      </div>
    </div>
    <ul tabindex="-1" class="dropdown-content menu bg-base-100 rounded-box z-1 w-52 p-2 shadow-lg">
      <li>
        <!--user-space-index:index.js中的，user_id是index.js中的path:'/user/space/:user_id/'中的，user.id是user.js中返回的id-->
        <RouterLink @click="closeMenu" :to="{name:'user-space-index',params:{user_id:user.id}}">
          <div class="avatar">
            <div class="w-10 rounded-full">
              <img :src="user.photo">
            </div>
          </div>
          <!--line-clamp-1最多1行，超过的变成省略号-->
          <span class="text-base font-bold line-clamp-1">{{user.username}}</span>
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
        <a @click="closeMenu" class="text-sm font-bold py-3">
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









