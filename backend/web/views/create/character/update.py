from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character, Voice
from web.views.utils.photo import remove_old_photo
from django.utils.timezone import now

class UpdateCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            character_id=request.data['character_id']
            # author__user是Django中跨关系查询的语法，表示通过author字段找到关联的UserProfile对象，再进一步找到它的user字段。
            # 双下划线__是Django中用来跨表查询的语法
            # user_id:user 对象的 id 字段,字段访问（获取值）
            # author__user:从 author(character表的字段) 跨表到 user 字段,跨表查询（用于过滤条件）
            character=Character.objects.get(id=character_id,author__user=request.user)
            name=request.data['name'].strip()
            voice_id=request.data['voice_id']
            profile=request.data['profile'].strip()[:100000]
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
            if photo:
                remove_old_photo(character.photo)
                character.photo=photo
            if background_image:
                remove_old_photo(character.background_image)
                character.background_image=background_image

            voice=Voice.objects.get(id=voice_id)

            character.name=name
            character.voice=voice
            character.profile=profile
            character.update_time=now()
            character.save()
            return Response({
                'result':'success'
            })
        except:
            return Response({
                'result':'系统异常,请稍后重试'
            })




















