import os.path

from django.conf import settings

def remove_old_photo(photo):
    if photo and photo.name!='user/photos/default.png':
        old_path=settings.MEDIA_ROOT / photo.name
        if os.path.exists(old_path):
            #os是一个工具包可以管理文件
            os.remove(old_path)