from django.utils.timezone import now
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from web.models.user import UserProfile
from web.views.utils.photo import remove_old_photo


class UpdateProfileView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user
            user_profile=UserProfile.objects.get(user=user)
            username=request.data.get('username').strip()
            profile=request.data.get('profile').strip()[:500]
            photo=request.FILES.get('photo',None)#从本次 HTTP 请求上传的文件列表中，获取名为 'photo' 的文件，如果找不到则返回 None，因为文件太大
            if not username:
                return Response({
                    'result':'用户名不能为空'
                })
            if not profile:
                return Response({
                    'result':'简介不能为空'
                })
            if username!=user.username and User.objects.filter(username=username).exists():
                return Response({
                    'result':'用户名已存在'
                })
            if photo:
                remove_old_photo(user_profile.photo)
                user_profile.photo=photo
            user_profile.profile=profile
            user_profile.update_time=now()
            user_profile.save()
            user.username=username
            user.save()
            # 前端有，但是后端又返回一次主要是因为后端返回了处理后的图片的url(名称改了)方便前端处理
            # 而且做一些额外操作比如删除原图片...
            return Response({
                'result':'success',
                'user_id':user.id,
                'username':user.username,
                'profile':user_profile.profile,
                'photo':user_profile.photo.url,
            })
        except:
            return Response({
                'result':'系统异常，请稍后重试'
            })