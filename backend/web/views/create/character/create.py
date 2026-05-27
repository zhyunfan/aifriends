from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character, Voice
from web.models.user import UserProfile

# APIView:DRF 提供的用于构建 api 的基类视图
# 怎么使用？	继承 APIView，定义 get()、post() 等方法
# URL 中怎么用？	CreateCharacterView.as_view()
class CreateCharacterView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,*args,**kwargs):
        try:
            user=request.user
            user_profile=UserProfile.objects.get(user=user)
            name=request.data.get('name').strip()
            voice_id=request.data.get('voice_id')#整数
            profile=request.data.get('profile').strip()[:100000]
            photo=request.FILES.get('photo',None)
            background_image=request.FILES.get('background_image',None)

            if not name:
                return Response({
                    'result':'名字不能为空'
                })
            if not profile:
                return Response({
                    'result':'角色介绍不能为空'
                })
            if not photo:
                return Response({
                    'result':'头像不能为空'
                })
            if not background_image:
                return Response({
                    'result':'聊天背景不能为空'
                })
            voice=Voice.objects.get(id=voice_id)
            # 插入一条新的角色（Character）记录
            Character.objects.create(
                author=user_profile,
                name=name,
                voice=voice,
                profile=profile,
                photo=photo,
                background_image=background_image,
            )
            return Response({
                'result':'success'
            })
        except:
            return Response({
                'result':'系统异常,请稍后重试'
            })













