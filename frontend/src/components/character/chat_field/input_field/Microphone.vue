<script setup lang="js">
import KeyboardIcon from "@/components/character/icons/KeyboardIcon.vue";
import {onBeforeUnmount, onMounted, ref} from "vue";
//内部使用的就是 Silero VAD，Silero VAD 训练数据几乎全是人类语音，
// Silero VAD 的训练数据集包含：
// - 98% 人类语音（各语言、口音、年龄）
// - 2% 背景噪音（用来增强鲁棒性）
// - 0% 动物声音（因为场景不需要）
import {MicVAD} from "@ricky0123/vad-web";//VAD（Voice Activity Detection）库，用于检测人声开始/结束
import api from "@/js/http/api.js";
import CONFIG_API from "@/js/config/config.js";

const emit=defineEmits(['close','send','stop'])
const isSpeaking=ref(false)

let vadInstance = null;

// 时间线（每帧 10ms）
// t=0ms    : 用户还没说话，VAD 静默监听，内部缓冲区持续循环
// t=200ms  : 用户说 "He"，VAD 检测到置信度 0.85 > 0.8
//            → 触发 onSpeechStart
//            → 清空旧缓冲区，开始记录新音频
// t=210ms  : "e" 音频帧 → 存入缓冲区
// t=220ms  : "l" 音频帧 → 存入缓冲区
// t=230ms  : "l" 音频帧 → 存入缓冲区
// t=240ms  : "o" 音频帧 → 存入缓冲区
// t=500ms  : 用户说完，开始静音
// t=510ms  : 静音帧1（置信度 0.2）
// t=520ms  : 静音帧2（置信度 0.1）
// t=530ms  : 静音帧3
// t=540ms  : 静音帧4
// t=550ms  : 静音帧5 → 达到 redemptionFrames=5
//            → 触发 onSpeechEnd
//            → 返回从 t=200ms 到 t=550ms 的所有音频数据

//非流式（Non-streaming）ASR，也叫一句话识别或语音文件识别
const startRecording = async () => {
  //vad/：服务器上的一个目录路径:frontend/public/vad
  // const baseUrl = "http://127.0.0.1:8000/static/frontend/vad/";
  const baseUrl = CONFIG_API.VAD_URL;
  try {
    // 1. 初始化 VAD 实例
    vadInstance = await MicVAD.new({
      //2. 模型文件路径,告诉 VAD 库去哪里找模型文件
      //ONNX (Open Neural Network Exchange) - 开放神经网络交换格式
      //WASM (WebAssembly) - 网页汇编语言
      // ort-wasm.wasm 是 ONNX Runtime 在 Web 中的运行环境,作用：在浏览器中执行 ONNX 模型的推理计算
      //ONNX 模型 (.onnx)
      //     ↓
      // ONNX Runtime (通过 WASM 在浏览器运行)
      //     ↓
      // CPU/GPU 执行计算
      //     ↓
      // 返回结果（是否有人声）
      baseAssetPath: baseUrl,
      // 3. 事件回调
      // 用户开始说话时触发
      onSpeechStart: () => {
        isSpeaking.value = true;// 显示波形动画
        emit('stop')// 通知父组件如果ai还在输出，终止上次对话
      },
      // 用户停止说话时触发
      //audio 参数是 VAD 库在 onSpeechStart 到 onSpeechEnd 期间自动缓存的音频数据，由库内部管理，你不需要手动传入
      onSpeechEnd: (audio) => {//audio（Float32Array 格式的音频数据）
        isSpeaking.value = false;// 隐藏波形动画
        const pcm16 = float32ToInt16(audio);// Float32 → PCM16
        sendToBackend(pcm16);// 发送给后端识别，只有这里才会调用大模型！
      },
      ortConfig: (ort) => {//ort 参数由 @ricky0123/vad-web 库内部传入
        ort.env.wasm.wasmPaths = baseUrl;// WebAssembly 文件也从这里加载
        ort.env.logLevel = "error";//设置 ONNX Runtime 的日志输出级别 "error"	只输出错误
      },
      positiveSpeechThreshold: 0.8,// 开始说话阈值 当 VAD 模型判断音频帧是语音的置信度超过 0.8 时，认为用户开始说话
      negativeSpeechThreshold: 0.65,//结束说话阈值 当置信度低于 0.65 时，认为用户可能停止说话了
      //避免短暂噪音（咳嗽、鼠标点击）误触发 每帧通常 10ms，5 帧 = 50ms 只有持续 50ms 的人声才认为是真正的说话
      minSpeechFrames: 5,//最少连续语音帧数 需要连续 5 帧 都被判定为语音，才真正触发 onSpeechStart
      redemptionFrames: 5,//缓冲帧数/容忍静音帧数 说话过程中，允许最多连续 5 帧 置信度低于阈值，仍认为在说话，否则 触发 onSpeechEnd
    });
    //不会立即调用大模型（只是准备就绪，等待你说话）
    await vadInstance.start();//正式启动 VAD（语音活动检测）引擎，开始监听麦克风并分析音频

  } catch (e) {
    console.error("VAD 初始化失败:", e);
  }
};
// 将 Float32 转 PCM 16-bit
const float32ToInt16 = (float32Array) => {//VAD 返回的是 Float32（范围 -1 ～ 1）
  //创建一个指定长度的 Int16 类型数组（16位有符号整数数组）
  const buffer = new Int16Array(float32Array.length);
  for (let i = 0; i < float32Array.length; i++) {
    let s = Math.max(-1, Math.min(1, float32Array[i]));
    //将 Float32（-1~1）映射到 Int16（-32768~32767）
    // 0x8000 = 32768 0x7FFF = 32767
    buffer[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  //后端通常需要 16-bit PCM（范围 -32768 ～ 32767）,线性映射并转为 ArrayBuffer
  //返回 Int16Array 底层的 ArrayBuffer 原始二进制数据，前面用十六进制是因为与二进制对应直观
  return buffer.buffer;
};

const sendToBackend = async (arrayBuffer) => {
  // 将音频发送到后端
  //将原始的 PCM 音频二进制数据包装成一个 Blob 对象，并标记为 PCM 音频格式
  //Blob = Binary Large Object（二进制大对象）是 File 对象的父类，用于在浏览器中表示二进制数据
  //用 [] 包裹是因为 Blob 可以接受多个数据源，// 多个数据源（会合并）
  //{ type: 'audio/pcm' } - MIME 类型，告诉浏览器这是什么类型的数据，audio/pcm 表示原始 PCM 音频格式
  //不使用 Blob 后端可能无法解析因为缺少文件信息（文件名、MIME类型等）
  const blob=new Blob([arrayBuffer],{type:'audio/pcm'})
  //FormData 的作用：模拟 HTML 表单提交，支持同时上传多个文件/字段，后端可以直接用 request.files['audio'] 获取
  const formData=new FormData()
  //告诉浏览器：我要在这个表单里上传一个文件，字段名叫 audio，文件内容在 blob 里，上传时建议的文件名叫 voice.pcm
  //'audio' —— 字段名（key）相当于表单里 <input name="audio"> 的 name
  //字段名	让后端知道“这个数据是什么”	快递盒上的物品类别（衣服 / 文件 / 电子产品）
  // 文件名	让后端知道“这个文件叫什么”	快递盒里的具体物品名称（牛仔裤 / 合同.pdf）
  formData.append('audio',blob,'voice.pcm')
  try{
    // 后端不是收到一个完整的 formData 对象，而是自动把它拆解到 request 的不同属性中：
    // 文件 → request.FILES
    // 普通文本字段 → request.POST 或 request.data
    const res=await api.post('/api/friend/message/asr/asr',formData)
    const data=res.data
    // console.log(data)
    if(data.result==='success'){
      emit('send',null,data.text)
    }
  }catch (err){
    console.error(err)//输出红色的
  }
};

onMounted(() => {
  startRecording()
})

onBeforeUnmount(() => {
  if (vadInstance) {
    vadInstance.destroy()
    vadInstance = null
  }
})
</script>

<template>
  <div class="absolute bottom-4 left-2 h-12 w-86 flex items-center bg-black/30 backdrop-blur-sm rounded-2xl">
    <div v-if="isSpeaking" class="flex items-center justify-center gap-1 h-6 flex-1">
      <div
        v-for="i in 32" :key="i"
        class="w-0.5 bg-blue-400 rounded-full animate-wave"
        :style="{ animationDelay: `${i * 0.1}s` }"
      ></div>
    </div>
    <div v-else class="text-white/50 text-base w-full text-center">
      语音输入
    </div>
    <!--当点击元素时，向外发射一个名为 'close' 的自定义事件-->
    <div @click="emit('close')" class="absolute right-2 w-8 h-8 flex justify-center items-center cursor-pointer">
      <KeyboardIcon></KeyboardIcon>
    </div>
  </div>
</template>

<style scoped>
.animate-wave {
  height: 4px;
  animation: wave-animation 0.6s ease-in-out infinite alternate;
}

@keyframes wave-animation {
  0% { height: 4px; opacity: 0.3; }
  100% { height: 20px; opacity: 1; }
}
</style>