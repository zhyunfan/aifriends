import json

from django.http import StreamingHttpResponse
from langchain_core.messages import HumanMessage, BaseMessageChunk
from rest_framework.renderers import BaseRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend
from web.views.friend.message.chat.graph import ChatGraph

# django的DRF不能直接返回sse需要伪渲染器
# DRF 默认支持的响应格式是 JSON、XML 等完整响应，而 SSE 是流式响应，两者不兼容
#  Django REST Framework
# 定义一个伪渲染器，防止 DRF 报错：
class SSERenderer(BaseRenderer):
    media_type = 'text/event-stream'
    format = 'txt'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

class MessageChatView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [SSERenderer]  # 引入渲染器
    def post(self,request):
        # 不加try,except否则不方便调试，报错看不见
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
        app=ChatGraph.create_app()
        inputs={'messages':[HumanMessage(message)]}
        # # invoke非流式回复,stream流式
        # res=app.invoke(inputs)
        # # 有2个元素，一个是HumanMessage(message)，一个是AIMessage
        # print(res['messages'][-1].content)

        # 定义一个流式生成器
        def event_stream():
            # 存储消耗量
            full_usage={}
            # stream流式回复，stream_mode="messages"	流模式：按消息粒度输出（不是按节点）
            # msg：当前收到的消息对象（通常是 AIMessageChunk）
            # metadata：消息的元数据（包含节点名、时间戳等信息）
            for msg,metadata in app.stream(inputs,stream_mode="messages"):
                # 是不是消息片段
                # BaseMessage	完整消息	一次性返回完整内容，不可变
                # BaseMessageChunk	消息块/片段	流式输出中的一小部分，可以拼接成完整消息
                if isinstance(msg,BaseMessageChunk):
                    # 判断是否有消息
                    if msg.content:
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
            print(full_usage)
        # # for循环会自动用next去迭代该生成器
        # for data in event_stream():
        #     print(data)
        # return Response({
        #     'result':'success',
        # })
        response=StreamingHttpResponse(event_stream(),content_type="text/event-stream")
        response['Cache-Control']='no-cache'
        return response










