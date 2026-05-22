from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Message


# 在大模型回复过程中，前端会一直输出消息，但是后端只有当消息回复完成后才会有消息
# 消息的动态加载
class GetHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            last_message_id=int(request.query_params.get('last_message_id'))
            friend_id=request.query_params.get('friend_id')
            queryset=Message.objects.filter(friend_id=friend_id,friend__me__user=request.user)
            # 有消息就是消息id没消息就是0
            if last_message_id>0:#不是第一次加载
                queryset=queryset.filter(pk__lt=last_message_id)#pk<last_message_id
            #拉取离last_message_id时间最近的信息
            messages_raw=queryset.order_by('-id')[:10]
            messages=[]
            for m in messages_raw:
                messages.append({
                    'id':m.id,
                    'user_message':m.user_message,
                    'output':m.output,
                })
            return Response({
                'result':'success',
                'messages':messages,
            })
        except:
            return Response({
                'result':'系统异常，请稍后重试'
            })