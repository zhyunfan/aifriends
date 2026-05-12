import uuid
from django.db import models
from django.utils.timezone import now, localtime

from web.models.user import UserProfile

def photo_upload_to(instance,filename):
    ext=filename.split('.')[-1]
    filename=f'{uuid.uuid4().hex[:10]}.{ext}'
    # user_id或者user.id只是user_id可以少一次数据库查询,instance表示Character对象
    return f'character/photos/{instance.author.user_id}_{filename}'

def background_image_upload_to(instance,filename):
    ext=filename.split('.')[-1]
    filename=f'{uuid.uuid4().hex[:10]}.{ext}'
    # user_id或者user.id只是user_id可以少一次数据库查询,instance表示Character对象
    return f'character/background_images/{instance.author.user_id}_{filename}'

class Character(models.Model):
    # 定义数据库字段，用于创建一个角色（Character）相关的数据表。
    # models.ForeignKey外键字段，表示一对多关系（一个用户可以创建多个角色）,关联到UserProfile模型,on_delete=models.CASCADE当关联的 UserProfile 被删除时，自动删除该作者创建的所有角色
    author=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    # CharField	字符串类型字段
    name=models.CharField(max_length=50)
    # ImageField图片类型字段（需要安装Pillow库）
    photo=models.ImageField(upload_to=photo_upload_to)
    # max_length最大行数没有用,需要自己截断(create.py)
    profile=models.TextField(max_length=100000)
    background_image=models.ImageField(upload_to=background_image_upload_to)
    create_time=models.DateTimeField(default=now)
    update_time=models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.author.user.username}-{self.name}-{localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"