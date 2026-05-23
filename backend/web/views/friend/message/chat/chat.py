import json
from pprint import pprint

from django.http import StreamingHttpResponse
from langchain_core.messages import HumanMessage, BaseMessageChunk, SystemMessage, AIMessage
from rest_framework.renderers import BaseRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend, Message, SystemPrompt
from web.views.friend.message.chat.graph import ChatGraph

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

        # 定义一个流式生成器
        def event_stream():
            full_output=''
            # 存储消耗量
            full_usage={}
            # stream流式回复，stream_mode="messages"	流模式：按消息粒度输出（不是按节点）
            # msg：当前收到的消息对象（通常是 AIMessageChunk）
            # metadata：消息的元数据（包含节点名、时间戳等信息）
            # 流式执行 LangGraph 应用，并逐条获取生成的消息。
            # inputs：初始输入数据（对话历史、用户消息等）
            # stream_mode="messages"：指定流式模式为"消息模式"
            for msg,metadata in app.stream(inputs,stream_mode="messages"):
                # 是不是消息片段
                # BaseMessage	完整消息	一次性返回完整内容，不可变
                # BaseMessageChunk	消息块/片段	流式输出中的一小部分，可以拼接成完整消息
                if isinstance(msg,BaseMessageChunk):
                    # 判断是否有消息
                    if msg.content:
                        full_output+=msg.content#因为是流式输出
                        # yield	生成器关键字，逐次返回数据，不一次性返回所有，即给前端发个消息,相当于return
                        # f'data:...\n\n'	SSE 标准格式：data: 前缀 + 两个换行符结尾
                        # json.dumps(...)	将 Python 字典转为 JSON 字符串
                        # {'content': msg.content}	包装成 JSON 对象，前端可以解析
                        # ensure_ascii=False	保留中文等非 ASCII 字符（不转义为 \uxxxx）默认为unicode
                        yield f'data:{json.dumps({'content':msg.content},ensure_ascii=False)}\n\n'
                    # usage_metadata 字段（Token 使用统计）
                    # # usage_metadata 的典型结构
                    # msg.usage_metadata = {
                    #     "input_tokens": 150,      # 输入消耗的 Token 数（你的问题）
                    #     "output_tokens": 80,      # 输出消耗的 Token 数（AI 的回答）
                    #     "total_tokens": 230,      # 总 Token 数
                    #     "cache_read_tokens": 0    # 可选：缓存命中的 Token 数（某些模型支持）
                    # }
                    # hasattr(msg,'usage_metadata'):检查消息对象是否包含 usage_metadata 这个属性
                    if hasattr(msg,'usage_metadata') and msg.usage_metadata:
                        full_usage=msg.usage_metadata
            yield 'data:[DONE]\n\n'
            input_tokens=full_usage.get('input_tokens',0)
            output_tokens=full_usage.get('output_tokens',0)
            total_tokens=full_usage.get('total_tokens',0)
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

        # StreamingHttpResponse：Django 提供的流式响应类，适合传输大文件或实时数据流。
        # event_stream()# 生成器函数，产生流式数据
        response=StreamingHttpResponse(event_stream(),content_type="text/event-stream")
        response['Cache-Control']='no-cache'#响应头禁止缓存
        return response










