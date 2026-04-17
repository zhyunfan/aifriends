from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


# 不需要登录
class RefreshTokenView(APIView):
    def post(self,request):
        try:
            refresh_token=request.COOKIES.get('refresh_token')
            if not refresh_token:
                return Response({
                    'result':'refresh token不存在'
                },status=401)#必须加401，前端判断时要用到
            # 通过一个已存在的刷新令牌字符串，创建 / 解析出一个RefreshToken对象实例
            # refresh_token本身是一个字符串,但当它过期或无效时传入的就是无效字符串（内部编码了过期时间信息（JWT 格式）），RefreshToken会对比当前时间
            refresh=RefreshToken(refresh_token)#如果refresh token过期了，会报异常从而捕获
            if settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS']:#设置为True那么当refresh刷新access时，refresh会重新延长期限为7天
                refresh.set_jti()#刷新
                response=Response({
                    'result':'success',
                    'access':str(refresh.access_token),
                })
                response.set_cookie(
                    key='refresh_token',
                    value=str(refresh),
                    httponly=True,
                    samesite='Lax',
                    secure=True,
                    max_age=86400 * 7,
                )
                return response
            return Response({
                'result':'success',
                'access':str(refresh.access_token),
            })
        except:
            return Response({
                'result':'refresh token过期了'
            },status=401)#必须加401










