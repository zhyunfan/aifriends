<script setup lang="ts">

import MenuIcon from "@/components/navbar/icons/MenuIcon.vue";
import HomepageIcon from "@/components/navbar/icons/HomepageIcon.vue";
import FriendIcon from "@/components/navbar/icons/FriendIcon.vue";
import CreateIcon from "@/components/navbar/icons/CreateIcon.vue";
import SearchIcon from "@/components/navbar/icons/SearchIcon.vue";
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
      <div class="navbar-center w-4/5 max-w-180">
        <!--搜索框-->
        <div class="join w-4/5">
          <input class="input join-item rounded-l-full w-4/5" placeholder="搜索你感兴趣的内容" />
          <button class="btn join-item rounded-r-full gap-0">
            <SearchIcon></SearchIcon>
            搜索
          </button>
        </div>
      </div>
      <!--右边-->
      <div class="navbar-end">
        <button class="btn btn-ghost text-lg">登录</button>
      </div>
    </nav>
    <slot></slot>
  </div>

  <div class="drawer-side is-drawer-close:overflow-visible">
    <label for="my-drawer-4" aria-label="close sidebar" class="drawer-overlay"></label>
    <div class="flex min-h-full flex-col items-start bg-base-200 is-drawer-close:w-16 is-drawer-open:w-54">
      <ul class="menu w-full grow">
        <li>
          <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="首页">
            <HomepageIcon></HomepageIcon>
            <!--whitespace-nowra不换行-->
            <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">首页</span>
          </button>
        </li>
        <li>
          <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="好友">
            <FriendIcon></FriendIcon>
            <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">好友</span>
          </button>
        </li>
        <li>
          <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="创作">
            <CreateIcon></CreateIcon>
            <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">创作</span>
          </button>
        </li>
      </ul>
    </div>
  </div>
</div>
</template>

<style scoped>

</style>