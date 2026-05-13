<script setup lang="js">
import {nextTick, onBeforeUnmount, ref, useTemplateRef, watch} from "vue";
import CameraIcon from "@/views/user/profile/components/icon/CameraIcon.vue";
import Croppie from 'croppie'
import 'croppie/croppie.css'

// 在 Vue 中，任何自定义标签（非原生 HTML 标签）都是子组件
// 表示ProfileIndex.vue中的<Photo :photo="user.photo"></Photo>
// props.photo 的值就是 user.photo 的值即user数据库中的photo，接下来会将其赋值给myPhoto,然后在页面上显示出来
//如果更改头像那么通过模态框裁剪下来点击确定更新数据库，和frontend/src/views/create/character/components/Photo.vue相比，
// 那个文件里面因为父组件CreateCharacter.vue没有设置:photo,所以刚开始为灰色图片（代码设置的）,之后选择图片点击确定就添加到数据库了
// defineProps定义子组件可以接收什么参数
const props=defineProps(['photo'])
// 需要用到响应式，因为裁剪图片那么myPhoto会变
const myPhoto=ref(props.photo)
// 同步传过来的组件和内部的组件
watch(()=>props.photo,newVal=>{
  myPhoto.value=newVal
})
// 获取模板中的 DOM 元素或组件实例
const fileInputRef=useTemplateRef('file-input-ref')
 // 用来获取模板中 ref="modal-ref" 的那个 DOM 元素或组件
// 模板中的 ref="modal-ref"	相当于给一个人起个外号叫 "小张"
const modalRef=useTemplateRef('modal-ref')
const croppieRef=useTemplateRef('croppie-ref')
//croppie不用显示在前端所以不用响应式变量
let croppie=null
async function openModal(photo){
  //所有的响应式变量在Javascript中使用时都需要.value再用其它操作,但是在html使用时不需要.value
  modalRef.value.showModal()//打开模态框
  //等所有元素渲染完之后,等待 DOM 更新完成
  await nextTick()

  if(!croppie){
    croppie = new Croppie(croppieRef.value, {  // 创建croppie对象
      viewport: {width: 200, height: 200, type: 'square'},
      boundary: {width: 300, height: 300},
      enableOrientation: true,
      enforceBoundary: true,
    })
  }
  // 将一张图片“绑定”到裁剪器上，也就是让裁剪器加载并显示你指定的图片，然后你就可以对这张图片进行裁剪操作了
  croppie.bind({
    url:photo,
  })
}
//裁剪图片
async function crop(){
  myPhoto.value = await croppie.result({  // 获取裁剪结果
    type: 'base64',
    size: 'viewport',
  })
  modalRef.value.close()
}
function onFileChange(e){
  const file=e.target.files[0]
  // 要不然第一次选择某图片，下次如果再次选择该图片那么就不会弹出模态框裁剪图片了
  e.target.value=''
  if(!file)return
  const reader=new FileReader()
  //读完时触发该函数
  reader.onload=()=>{
    //打开一个模态框用来裁剪图片,在daisyui.com中找一个:modal
    //执行上面定义的openModal函数
    openModal(reader.result)
  }
  reader.readAsDataURL(file)//会读取成base64的形式
}
//组件卸载前
onBeforeUnmount(() => {  // 释放croppie对象，防止内存泄漏
  //?表示如果前面是空就返回空不执行后面的.操作即.destroy()了
  croppie?.destroy()
})
//将myPhoto暴露出去,那么父组件就可以用myPhoto
defineExpose({
  myPhoto,
})
</script>

<template>
  <div class="flex justify-center">
    <div class="avatar relative">
      <div class="w-28 rounded-full ">
        <img :src="myPhoto" alt="">
      </div>
      <div @click="fileInputRef.click()" class="absolute left-0 top-0 w-28 h-28 flex justify-center items-center bg-black/20 rounded-full cursor-pointer">
          <CameraIcon ></CameraIcon>
      </div>
    </div>
  </div>
  <input ref="file-input-ref" type="file" accept="image/*" class="hidden" @change="onFileChange">
  <dialog ref="modal-ref" class="modal">
    <!--加了transition-none那么如果放大图片截取右下角就会对齐了-->
    <div class="modal-box transition-none">
      <!--这里不需要在父组件加relative是因为modal中已经定义了absolute的父组件必须加的样式了
      modalRef.close()不需要.value再close了-->
      <button @click="modalRef.close()" class="btn btn-circle btn-sm btn-ghost absolute right-2 top-2">✕</button>
      <!--裁剪功能需要绑定在一个组件中-->
      <div ref="croppie-ref" class="flex flex-col justify-center my-4"></div>
      <div class="modal-action">
        <button @click="modalRef.close()" class="btn">取消</button>
        <button @click="crop" class="btn btn-neutral">确定</button>
      </div>
    </div>
  </dialog>
</template>

<style scoped>

</style>














