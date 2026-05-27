const platform='vue'//一共3个模式，前端vue,后端django,上线cloud

const CONFIG_API={
    HTTP_URL:'',//在/http/api.js和http/streamApi.js里面的URL
    VAD_URL:'',//在fronted/src/components/character/chat_field/input_field/Microphone.vue中的一个vad路径
}

if(platform==='vue'){
    CONFIG_API.HTTP_URL='http://127.0.0.1:8000'
    CONFIG_API.VAD_URL="http://localhost:5173/vad/"
}else if(platform==='django'){
    CONFIG_API.HTTP_URL='http://127.0.0.1:8000'
    CONFIG_API.VAD_URL="http://127.0.0.1:8000/static/frontend/vad/"
}else if(platform==='cloud'){
    CONFIG_API.HTTP_URL='https://app7956.acapp.acwing.com.cn'
    CONFIG_API.VAD_URL="https://app7956.acapp.acwing.com.cn/static/frontend/vad/"
}
export default CONFIG_API