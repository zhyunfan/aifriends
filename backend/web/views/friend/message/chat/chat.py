from langchain_core.messages import HumanMessage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend
from web.views.friend.message.chat.graph import ChatGraph


class MessageChatView(APIView):
    permission_classes = [IsAuthenticated]
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
        res=app.invoke(inputs)
        # 有2个元素，一个是HumanMessage(message)，一个是AIMessage
        print(res['messages'])[-1].content
        return Response({
            'result':'success',
        })

