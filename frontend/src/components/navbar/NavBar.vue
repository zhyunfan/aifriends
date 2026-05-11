<script setup lang="js">

import MenuIcon from "@/components/navbar/icons/MenuIcon.vue";
import HomepageIcon from "@/components/navbar/icons/HomepageIcon.vue";
import FriendIcon from "@/components/navbar/icons/FriendIcon.vue";
import CreateIcon from "@/components/navbar/icons/CreateIcon.vue";
import SearchIcon from "@/components/navbar/icons/SearchIcon.vue";
import {useUserStore} from '@/stores/user'
import UserMenu from "@/components/navbar/UserMenu.vue";

const user=useUserStore()
</script>

<template>
<div class="drawer lg:drawer-open">
  <input id="my-drawer-4" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content">
    <!--shadow-sm阴影 shadow-white白色阴影-->
    <nav class="navbar w-full bg-base-300 shadow-white shadow-sm">
      <!--导航栏左边-->
      <div class="navbar-start">
        <label for="my-drawer-4" aria-label="open sidebar" class="btn btn-square btn-ghost">
          <MenuIcon></MenuIcon>
        </label>
        <!--font-bold加粗 text-2xl变大 px-2内边距 x:水平即左右 my:外边距 上下 pt pr pb pl-->
        <div class="px-2 font-bold text-2xl">AIFriends</div>
      </div>
      <!--中间-->
      <!--flex设置display: flex将元素变为弹性容器 justify-center主轴方向居中排列子元素
      items-center:垂直居中-->
      <div class="navbar-center w-4/5 max-w-180 flex justify-center">
        <!--搜索框-->
        <div class="join w-4/5 flex justify-center">
          <input class="input join-item rounded-l-full w-4/5" placeholder="搜索你感兴趣的内容" />
          <button class="btn join-item rounded-r-full gap-0">
            <SearchIcon></SearchIcon>
            搜索
          </button>
        </div>
      </div>
      <!--右边-->
      <div class="navbar-end">
        <RouterLink v-if="user.isLogin()" :to="{name:'create-index'}" class="btn btn-ghost text-base mr-6">
          <CreateIcon></CreateIcon>创作
        </RouterLink>
<!--        user.hasPulledUserInfo防止登录后刷新闪过登录字样-->
        <RouterLink v-if="user.hasPulledUserInfo&&!user.isLogin()" :to="{name:'user-account-login-index'}" active-class="btn-active" class="btn btn-ghost text-lg">
          登录</RouterLink>
        <!--v-else表示如果前面成立显示登录，不成立显示UserMenu
        即 否则就渲染这个，v-else 必须紧跟在 v-if/v-else-if 后面-->
        <UserMenu v-else-if="user.isLogin()"></UserMenu>
      </div>
    </nav>
    <slot></slot>
  </div>

  <div class="drawer-side is-drawer-close:overflow-visible">
    <label for="my-drawer-4" aria-label="close sidebar" class="drawer-overlay"></label>
    <div class="flex min-h-full flex-col items-start bg-base-200 is-drawer-close:w-16 is-drawer-open:w-54">
      <ul class="menu w-full grow">
        <li>
          <!--menu-focus高亮
          active-class="menu-focus"：当 <RouterLink> 的 URL 与当前路由匹配时，自动给这个链接添加指定的类名（这里是 menu-focus添加到class中），用于高亮显示当前所在的菜单项。-->
          <RouterLink :to="{name:'homepage-index'}" active-class="menu-focus" class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="首页">
            <HomepageIcon></HomepageIcon>
            <!--whitespace-nowra不换行-->
            <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">首页</span>
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{name:'friend-index'}" active-class="menu-focus" class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="好友">
            <FriendIcon></FriendIcon>
            <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">好友</span>
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{name:'create-index'}" active-class="menu-focus" class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="创作">
            <CreateIcon></CreateIcon>
            <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">创作</span>
          </RouterLink>
        </li>
      </ul>
    </div>
  </div>
</div>
</template>

<style scoped>

</style>