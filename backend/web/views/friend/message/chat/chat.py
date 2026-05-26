import asyncio
import base64
import json
import os
import threading
import uuid
from pprint import pprint
from queue import Queue

import websockets
from django.http import StreamingHttpResponse
from langchain_core.messages import HumanMessage, BaseMessageChunk, SystemMessage, AIMessage
from openai import api_key
from rest_framework.renderers import BaseRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend, Message, SystemPrompt
from web.views.friend.message.chat.graph import ChatGraph
from web.views.friend.message.memory.update import update_memory


# django的DRF不能直接返回sse需要伪渲染器
# DRF 默认支持的响应格式是 JSON、XML 等完整响应，而 SSE 是流式响应，两者不兼容
# DRF: Django REST Framework
# 定义一个伪渲染器，防止 DRF 报错：
# DRF 默认的渲染器（如 JSONRenderer）会将数据转换为 JSON 格式，但 SSE 需要特殊的 text/event-stream 格式。这个渲染器告诉 DRF：不要处理数据，直接原样返回
# 继承 DRF 的 BaseRenderer 基类，创建一个自定义渲染器。
class SSERenderer(BaseRenderer):
    media_type = 'text/event-stream' # SSE 的 MIME 类型,设置响应的 Content-Type 头为 text/event-stream，告诉浏览器这是一个 SSE 流。
    format = 'txt'# 渲染器的标识符，可以在视图中通过 ?format=txt 指定使用这个渲染器
    # 重写渲染方法，直接返回原始数据，不做 JSON 序列化或其他转换
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

def add_system_prompt(state,friend):
    # 之前已有的信息 e.g. graph.py中的model_call的参数,
    #但是和graph.py中的信息不同的是，graph.py中添加信息时设置了状态图新信息会自动追加到信息末尾，这里该函数不会加到状态图里，状态图里的函数才会自动追加
    msgs=state['messages']
    system_prompts=SystemPrompt.objects.filter(title='回复').order_by('order_number')
    prompt=''
    for sp in system_prompts:
        prompt+=sp.prompt
    prompt+=f'\n【角色性格】\n{friend.character.profile}\n'
    # 将长期记忆加到系统提示词里
    prompt+=f'【长期记忆】\n{friend.memory}\n'
    # msgs 是一个列表（包含已有的 HumanMessage、AIMessage 等）
    # [SystemMessage(prompt)] 变成列表是因为需要和 msgs（也是一个列表）进行列表拼接操作。
    # [SystemMessage(prompt)] 是一个只包含一个元素的列表
    return {'messages':[SystemMessage(prompt)]+msgs}#创建系统消息对象,就是给 AI 看的"剧本"，告诉 AI 它应该扮演什么角色、遵守什么规则

#加上最近的10条对话
def add_recent_messages(state,friend):
    msgs=state['messages']
    #要把数据翻转需要变成list
    message_raw=list(Message.objects.filter(friend=friend).order_by('-id')[:10])
    message_raw.reverse()
    messages=[]
    for message in message_raw:
        #分别加用户信息和ai信息
        messages.append(HumanMessage(message.input))
        messages.append(AIMessage(message.output))
    #加到系统信息和用户问题中间，即有2个元素
    return {'messages':msgs[:1]+messages+msgs[-1:]}

class MessageChatView(APIView):
    # DRF 框架层面的配置属性，由 DRF 内部自动读取和使用
    permission_classes = [IsAuthenticated]
    renderer_classes = [SSERenderer]  # 引入渲染器# 渲染器：使用 SSE 格式
    def post(self,request):
        # 不加try,except否则不方便调试，报错看不见只能看见500这个错误
        friend_id=request.data['friend_id']
        message=request.data['message'].strip()
        if not message:
            return Response({
                'result':'消息不能为空'
            })
        # pk相当于id
        friends=Friend.objects.filter(pk=friend_id,me__user=request.user)
        if not friends.exists():
            return Response({
                'result':'好友不存在'
            })
        friend=friends.first()
        # app 是一个可执行的状态图
        app=ChatGraph.create_app()
        inputs={'messages':[HumanMessage(message)]}
        inputs=add_system_prompt(inputs,friend)
        inputs=add_recent_messages(inputs,friend)
        # 自动对数据结构进行格式化、缩进和换行，让输出更易读。
        # pprint(inputs)
        # # invoke非流式回复,stream流式
        # res=app.invoke(inputs)
        # # 有2个元素，一个是HumanMessage(message)，一个是AIMessage
        # print(res['messages'][-1].content)


        # StreamingHttpResponse：Django 提供的流式响应类，适合传输大文件或实时数据流。
        # event_stream()# 生成器函数，产生流式数据
        response=StreamingHttpResponse(
            self.event_stream(app,inputs,friend,message),
            content_type="text/event-stream"
        )
        response['Cache-Control']='no-cache'#响应头禁止缓存
        #不要Nginx缓存，要不然就看不到流式输出的效果
        response['X-Accel-Buffering'] = 'no'
        return response

    async def tts_sender(self,app,inputs,mq,ws,task_id):
        # stream流式回复，stream_mode="messages"	流模式：按消息粒度输出（不是按节点）
        # msg：当前收到的消息对象（通常是 AIMessageChunk）
        # metadata：消息的元数据（包含节点名、时间戳等信息）
        # 流式执行 LangGraph 应用，并逐条获取生成的消息。
        # inputs：初始输入数据（对话历史、用户消息等）
        # stream_mode="messages"：指定流式模式为"消息模式"
        # 下面改成异步版本：for msg, metadata in app.stream(inputs, stream_mode="messages"):同步迭代器
        # 异步迭代器：等待数据时，控制权让给“其他协程”，而不是“同代码块的下一个迭代器”
        async for msg, metadata in app.astream(inputs, stream_mode="messages"):#将用户问题给app，产生ai答案文本，下面顺便把ai答案文本加入队列，然后把文本发送给语音合成大模型，tts_receiver可以得到语音合成的音频数据，在tts_receiver函数中将音频数据加入队列
            # 是不是消息片段
            # BaseMessage	完整消息	一次性返回完整内容，不可变
            # BaseMessageChunk	消息块/片段	流式输出中的一小部分，可以拼接成完整消息
            if isinstance(msg, BaseMessageChunk):
                # 判断是否有消息
                if msg.content:
                    await ws.send(json.dumps({
                        "header": {
                            "action": "continue-task",
                            "task_id": task_id,
                            "streaming": "duplex"
                        },
                        "payload": {
                            "input": {
                                "text": msg.content,
                            }
                        }
                    }))
                    # 将一条消息以非阻塞的方式放入队列中,非阻塞方式放入数据，队列满时立即抛异常,不会死锁
                    mq.put_nowait({'content':msg.content})
                    # print(msg.content)#是文本内容
                # usage_metadata 字段（Token 使用统计）
                # # usage_metadata 的典型结构
                # msg.usage_metadata = {
                #     "input_tokens": 150,      # 输入消耗的 Token 数（你的问题）
                #     "output_tokens": 80,      # 输出消耗的 Token 数（AI 的回答）
                #     "total_tokens": 230,      # 总 Token 数
                #     "cache_read_tokens": 0    # 可选：缓存命中的 Token 数（某些模型支持）
                # }
                # hasattr(msg,'usage_metadata'):检查消息对象是否包含 usage_metadata 这个属性
                if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                    mq.put_nowait({'usage':msg.usage_metadata})
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

    #接收数据
    async def tts_receiver(self,mq,ws):
        async for msg in ws:#TTS 服务的主要输出是二进制音频
            if isinstance(msg,bytes):#接收的是字节数据就表示是音频
                # sse支持文本数据，所以把二进制转为文本，但是体积会变成4/3
                # 看起来像乱码，但实际是合法的 ASCII 字符
                # PCM 音频数据（16字节）bytes([0x00, 0x01, 0x02, 0x03,...]-->输出: AAECAwH+/v38f4CBggAAAAA=
                audio=base64.b64encode(msg).decode('UTF-8')
                mq.put_nowait({'audio':audio})
                print(audio)
            else:
                data=json.loads(msg)
                event=data['header']['event']
                if event in ['task-finished','task-failed']:
                    break

    #协程函数，关于音频合成的
    async def run_tts_tasks(self,app,inputs,mq):
        task_id=uuid.uuid4().hex
        api_key=os.getenv('API_KEY')
        wss_url=os.getenv('WSS_URL')
        headers={
            "Authorization": f"Bearer {api_key}"
        }
        #定义一个异步的websocket
        async with websockets.connect(wss_url,additional_headers=headers) as ws:
            await ws.send(json.dumps({
                "header": {
                    "action": "run-task",
                    "task_id": task_id,
                    "streaming": "duplex"
                },
                "payload": {
                    "task_group": "audio",
                    "task": "tts",
                    "function": "SpeechSynthesizer",
                    "model": "cosyvoice-v3-flash",
                    "parameters": {
                        "text_type": "PlainText",
                        "voice": "longanyang",  # 音色
                        "format": "mp3",  # 音频格式
                        "sample_rate": 22050,  # 采样率
                        "volume": 50,  # 音量
                        "rate": 1.25,  # 语速
                        "pitch": 1.0,  # 音调
                        "enable_ssml": False
                    },
                    "input": {}
                }
            }))
            async for msg in ws:
                if json.loads(msg)['header']['event']=='task-started':
                    break
            #同时等待两个线程结束
            await asyncio.gather(
                self.tts_sender(app,inputs,mq,ws,task_id),
                self.tts_receiver(mq,ws),#不需要返回数据，因为数据存在消息队列里
            )

    # 副线程里面需要定义2个协程
    # 在 Python 中，所有参数都是引用传递（更准确地说，是"对象引用传递"）
    def work(self,app,inputs,mq):
        try:
            # asyncio.run() 是运行协程
            asyncio.run(self.run_tts_tasks(app,inputs,mq))
        finally:
            # put_nowait()	立即放入，如果队列满了就抛异常	结束标记必须放进去，不能被阻塞
            # put()	如果队列满了就等待	生产者-消费者正常工作时
            # put_nowait 是为了避免死锁：如果队列满了，put() 会一直等，而消费者可能在等结束标记，形成死锁。
            # 告诉消费者：没有更多数据了，可以结束了,即如果队列满了 → 抛异常，你可以捕获并处理（比如重试或报错）
            mq.put_nowait(None)# 无论成功还是失败，最后都放入 None 作为结束信号

    # 定义一个流式生成器
    # 单拎出来，因为语音合成事件流很长，方便维护代码
    def event_stream(self,app,inputs,friend,message):
        # 创建消息队列
        mq=Queue()
        # 定义一个线程(副线程)
        thread=threading.Thread(target=self.work,args=(app,inputs,mq))
        thread.start()

        full_output=''
        # 存储消耗量
        full_usage={}
        while True:
            # 从消息队列中取数据,有ai回答的文本和音频数据
            msg=mq.get()
            if not msg:
                break
            if msg.get('content',None):
                full_output+=msg['content']
                # msg['content']	字典键访问	msg 是 dict 类型
                # msg.content	属性访问	msg 是 对象 类型
                yield f'data:{json.dumps({'content': msg['content']}, ensure_ascii=False)}\n\n'
            if msg.get('audio',None):
                full_usage['audio']=msg['audio']
                yield f'data:{json.dumps({'audio': msg['audio']}, ensure_ascii=False)}\n\n'
            if msg.get('usage',None):#token usage
                full_usage=msg['usage']


        yield 'data:[DONE]\n\n'
        input_tokens = full_usage.get('input_tokens', 0)
        output_tokens = full_usage.get('output_tokens', 0)
        total_tokens = full_usage.get('total_tokens', 0)
        Message.objects.create(
            friend=friend,
            user_message=message[:500],
            # 用于将 Python 对象（字典、列表、字符串等）转换为 JSON 格式的字符串，不过中文会被转义，需要ensure_ascii这样中文不会转义为unicode
            input=json.dumps(
                # m.model_dump()自动把里面的对象变成字典
                [m.model_dump() for m in inputs['messages']],
                ensure_ascii=False,
            )[:10000],
            output=full_output[:500],
            total_tokens=total_tokens,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        # print(full_usage)
        # # for循环会自动用next去迭代该生成器
        # for data in event_stream():
        #     print(data)
        # return Response({
        #     'result':'success',
        # })
        # 相当于每输出10条更新一次记忆，因为update_memory中的messages是取最近的10条
        if Message.objects.filter(friend=friend).count() % 1 == 0:
            update_memory(friend)










