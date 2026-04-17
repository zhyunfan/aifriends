from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class LogoutView(APIView):
    # permission_classesDRF视图属性，指定访问该接口需要的权限类列表
    # [IsAuthenticated]权限类之一：要求用户必须已通过身份认证（即已登录）
    permission_classes = [IsAuthenticated]#强制必须登录才能访问
    def post(self,request):
        response=Response({
            'result':'success',
        })
        response.delete_cookie('refresh_token')
        return response