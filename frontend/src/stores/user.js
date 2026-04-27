import {defineStore} from "pinia";
import {ref} from "vue";

// defineStore 返回的是一个函数
export const useUserStore=defineStore('user',()=>{
    const id=ref(1)
    const username=ref('zyf')
    const photo=ref('http://127.0.0.1:8000/media/user/photos/default.png')
    const profile=ref('111')
    const accessToken=ref('111')
    function isLogin(){
        return !!accessToken.value//必须带value否则accessToken永远不空，!!取非再取非
    }
    function setAccessToken(token){
        accessToken.value=token
    }
    // data相当于backend/web/views/user/account/login.py中的Response中的内容
    function setUserInfo(data){
        id.value=data.user_id
        username.value=data.username
        photo.value=data.photo
        profile.value=data.profile
    }
    function logout(){
        id.value=0
        username.value=''
        photo.value=''
        profile.value=''
        accessToken.value=''
    }
    return {
        id,
        username,
        photo,
        profile,
        accessToken,
        isLogin,
        setAccessToken,
        setUserInfo,
        logout
    }
})