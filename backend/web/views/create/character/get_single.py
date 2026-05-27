from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character, Voice


class GetSingleCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    # 没有任何修改操作,所以是get
    def get(self,request):
        try:
            # get方法传入的参数在request.query_params中；post方法传入的参数在request.data中
            character_id=request.query_params.get('character_id')
            character=Character.objects.get(id=character_id,author__user=request.user)

            voices_raw=Voice.objects.order_by("id")
            voices=[]
            for voice in voices_raw:
                voices.append({
                    'id':voice.id,
                    'name':voice.name,
                })

            return Response({
                'result':'success',
                'character':{
                    'id':character.id,
                    'name':character.name,
                    'photo':character.photo.url,
                    'profile':character.profile,
                    'background_image':character.background_image.url,
                    # 该id不是voice_id是系统自带的id即localhost/admin/web/voice/2/change中的2
                    #返回那个voice_id也行但是会暴露一些信息
                    'voice_id':character.voice.id,
                },
                'voices':voices,
            })
        except:
            return Response({
                'result':'系统异常,请稍后重试'
            })






