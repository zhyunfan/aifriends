import asyncio
import json
import os
import uuid

import websockets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class ASRView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        # FILES	专门存放上传文件的字典（类似 dict）
        # JSON/Form	request.data['friend_id']	文本/数字/JSON	普通表单数据、API 参数
        # 文件上传	request.FILES.get('audio')	二进制文件	图片、音频、视频等文件
        #  Django 把普通字段和文件字段分开存储
        # request.data / request.POST → 文本/数字等普通字段
        # request.FILES → 二进制文件数据
        audio=request.FILES.get('audio')
        if not audio:
            return Response({
                'result':'音频不存在'
            })
        # 从上传的音频文件对象中读取全部的二进制数据
        pcm_data=audio.read()
        # 同步地执行一个异步函数 run_asr_tasks，并将返回的结果赋值给 text 变量
        # asyncio.run(...)	同步等待异步任务完成
        # asyncio.run() 是运行协程,同步等待，必须等 协程函数self.run_asr_tasks() 完成后才会执行下一行代码
        text=asyncio.run(self.run_asr_tasks(pcm_data))
        return Response({
            'result':'success',
            'text':text,
        })

    #发送音频二进制数据的协程
    async def asr_sender(self,pcm_data,ws,task_id):
        #阿里云每次发二进制数据，建议每次发送100ms音频，并间隔100ms
        #阿里云一秒执行16000次，因为pcm16位2字节，所以一秒执行32000字节，那么100ms即0.1s执行3200字节
        # 因为实际上识别速度远大于说话速度所以我们等待10ms
        #所以推荐块的大小3200
        chunk=3200
        for i in range(0,len(pcm_data),chunk):
            await ws.send(pcm_data[i:i+chunk])
            await asyncio.sleep(0.01)
        # 发送finish-task
        await ws.send(json.dumps({
            "header": {
                "action": "finish-task",
                "task_id": task_id,
                "streaming": "duplex"
            },
            "payload": {
                "input": {}
            }
        }))


    # 服务器返回的 JSON 文本消息
    async def asr_receiver(self,ws):
        text=''
        async for msg in ws:
            # 把数据变成json字段
            data=json.loads(msg)
            event=data['header']['event']
            if event=='result-generated':
                output=data['payload']['output']
                if output.get('transcription',None) and output['transcription']['sentence_end']:
                    text+=output['transcription']['text']
            elif event in ['task-finished','task-failed']:
                break
        return text

    async def run_asr_tasks(self,pcm_data):
        # 生成一个随机的、唯一的字符串作为任务ID
        # uuid	Python 内置的 UUID 库
        # uuid4()	生成随机 UUID（版本4）
        # .hex	将 UUID 转为 32位十六进制字符串（不含连字符）
        task_id=uuid.uuid4().hex
        api_key=os.getenv('API_KEY')
        wss_url=os.getenv('WSS_URL')
        # 部分	            含义	                示例
        # 'Authorization'	HTTP 标准认证头字段	告诉服务器"我是来认证的"
        # 'Bearer'	认证方案（令牌认证）	表示使用令牌（Token）方式
        # {api_key}	实际的 API 密钥	sk-abc123xyz
        # 持有这个令牌的人就可以访问
        headers={
            'Authorization':f'Bearer {api_key}'
        }
        # 建立 WebSocket 连接
        # as ws	连接对象，用于收发消息
        async with websockets.connect(wss_url,additional_headers=headers) as ws:
            # 发送启动任务请求run-task
            await ws.send(json.dumps({#run-task的格式在官网找，语音识别的文档的输入在后边，输出在前边
                "header": {
                    "streaming": "duplex",  # 双工流式传输（可同时发送音频和接收结果）
                    "task_id": task_id,  # 任务唯一ID
                    "action": "run-task"  # 动作：运行任务
                },
                "payload": {
                    "model": "gummy-realtime-v1",  # 使用的模型
                    "parameters": {
                        "sample_rate": 16000,  # 采样率
                        "format": "pcm",  # 音频格式
                        "transcription_enabled": True,  # 启用转写（语音→文字）
                    },
                    "input": {},  # 输入数据（音频流在这里）是空的，音频数据会在连接建立后单独发送。
                    "task": "asr",  # 任务类型：语音识别
                    "task_group": "audio",  # 任务组：音频
                    "function": "recognition"  # 功能：识别
                }
            }))
            #需要等待发送task-started的事件
            # ws是异步连接，一旦遇到网络请求，就会挂起直到收到结果为止会再继续执行，异步请求要用异步循环
            # ws产生的是异步迭代器
            # 为什么需要这个循环？
            # WebSocket 是异步的：发送请求后，不会立即收到响应,服务器需要时间处理并返回 task-started 事件,必须等待这个确认才能继续发送音频
            # run-task输出：
            # {
            #   'header':{
            #       'task_id':'...',
            #       'event':'task-started',
            #       'attributes':{},
            #   },
            #   'payload':{}
            # }
            # 以下的语句要在ws定义的块内执行，因为如果在块外虽然对于python语句也可以执行，但是这里接收到的数据不完整，因为如果块一旦执行完之后，websocket就关闭了就得不到其它消息了
            async for msg in ws:#异步地、一条一条地接收 WebSocket 发来的消息
                # 把 JSON 字符串转成 Python 字典
                if json.loads(msg)['header']['event']=='task-started':
                #       ↑             ↑        ↑            ↑
                #    解析JSON         取header  取event     目标值
                    break
            #之后就可以进行发数据了
            # 同时执行多个协程，直到都执行完为止
            _,text=await asyncio.gather(
                self.asr_sender(pcm_data,ws,task_id),
                self.asr_receiver(ws),
            )
            return text