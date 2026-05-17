# 获取用户信息和角色列表，不需要登录，参考网上看up主时可以看到它发布的内容
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from web.models.character import Character
from web.models.user import UserProfile


class GetListCharacterView(APIView):
    def get(self, request):
        try:
            # 前端传来的是字符串，需要转换
            items_count=int(request.query_params.get('items_count'))
            # 不用转换是因为虽然是字符串，但是User.objects.get(id=user_id)中django查询时会自动把字符串转换为int
            user_id=request.query_params.get('user_id')
            user=User.objects.get(id=user_id)
            user_profile=UserProfile.objects.get(user=user)
            # -id表示倒序排 [items_count:items_count+20]左闭右开
            # Character.objects 操作Character模型（数据库表）的入口
            characters_raw=Character.objects.filter(author=user_profile).order_by('-id')[items_count:items_count+20]
            characters=[]
            for character in characters_raw:
                author=character.author
                characters.append({
                    'id': character.id,
                    'name': character.name,
                    'profile': character.profile,
                    'photo': character.photo.url,
                    'background_image': character.background_image.url,
                    # 卡片(每个发布的角色)里面只会用到作者的用户名不用作者简介所以不加profile
                    # 不过首页的卡片作者就不是统一的
                    'author':{
                        'user_id':author.user_id,
                        'username':author.user.username,
                        'photo':author.photo.url,
                    }
                })
            return Response({
                'result':'success',
                # 个人空间里需要返回用户信息（在顶部）即简介
                'user_profile':{
                    'user_id':user.id,
                    'username':user.username,
                    'profile':user_profile.profile,
                    'photo':user_profile.photo.url,
                },
                'characters':characters
            })
        except:
            return Response({
                'result':'系统异常，请稍后重试'
            })











