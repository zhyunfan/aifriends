from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character


class GetSingleCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    # 没有任何修改操作,所以是get
    def get(self,request):
        try:
            # get方法传入的参数在request.query_params中；post方法传入的参数在request.data中
            character_id=request.get_param('character_id')
            character=Character.objects.get(id=character_id,author__user=request.user)
            return Response({
                'result':'success',
                'character':{
                    'id':character.id,
                    'name':character.name,
                    'photo':character.photo.url,
                    'profile':character.profile,
                    'background_image':character.background_image,
                }
            })
        except:
            return Response({
                'result':'系统异常,请稍后重试'
            })






