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

class Voice(models.Model):
    name=models.CharField(max_length=100)
    # 是阿里云文档里面的名字
    voice_id=models.CharField(max_length=100)
    create_time=models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.name}-{self.voice_id}-{localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"

class Character(models.Model):
    # 定义数据库字段，用于创建一个角色（Character）相关的数据表。
    # models.ForeignKey外键字段，表示一对多关系（一个用户可以创建多个角色）,关联到UserProfile模型,on_delete=models.CASCADE当关联的 UserProfile 被删除时，自动删除该作者创建的所有角色
    author=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    # CharField	字符串类型字段
    name=models.CharField(max_length=50)
    # ImageField图片类型字段（需要安装Pillow库）
    photo=models.ImageField(upload_to=photo_upload_to)
    # blank=True	表单验证时允许为空（Django Admin 和 ModelForm）
    # null=True	数据库层面允许为空（数据库字段可为 NULL）
    voice=models.ForeignKey(Voice,default=None,on_delete=models.CASCADE,blank=True,null=True)
    # max_length最大行数没有用,需要自己截断(create.py)
    profile=models.TextField(max_length=100000)
    background_image=models.ImageField(upload_to=background_image_upload_to)
    create_time=models.DateTimeField(default=now)
    update_time=models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.author.user.username}-{self.name}-{localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"