from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from web.models.character import Character


class HomepageIndexView(APIView):
    def get(self,request):
        try:
            items_count=int(request.query_params.get('items_count'))
            search_query=request.query_params.get('search_query','').strip()
            if search_query:
                queryset=Character.objects.filter(
                    # 表示名字里包含search_query或者简介里包含search_query
                    # 名字匹配或profile匹配，contains表示是否匹配，i表示忽略大小写后是否匹配
                    Q(name__icontains=search_query)|Q(profile__icontains=search_query)
                )
            else:
                queryset=Character.objects.all()
            characters_row=queryset.order_by('-id')[items_count:items_count+20]
            characters=[]
            print('.'*9)
            for character in characters_row:
                print(character.name)
                author=character.author
                characters.append({
                    'id':character.id,
                    'name':character.name,
                    'profile':character.profile,
                    'photo':character.photo.url,
                    'background_image':character.background_image.url,
                    'author':{
                        'user_id':author.user_id,
                        'username':author.user.username,
                        'photo':author.photo.url,
                    }
                })
            return Response({
                'result':'success',
                'characters':characters
            })
        except:
            return Response({
                'result':'系统异常，请稍后重试'
            })













