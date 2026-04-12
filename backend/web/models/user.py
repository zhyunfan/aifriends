import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now, localtime


# 定义上传图片的名字
# filename：文件路径
# instance：数据库对象
# 随机字符串确保不同用户上传同名文件不会冲突
def photo_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    # uuid.uuid4().hex
    # uuid4() 随机生成一个全局唯一ID（UUID）。
    # .hex 把这个ID转成32位的十六进制字符串（只包含0 - 9，a - f，没有横杠）。
    # f'{...}.{ext}'
    # 一个f - string格式化字符串。
    # 把上面得到的前10位随机字符串作为文件名主体，ext（文件扩展名，比如jpg、pdf、txt）拼接到后面
    filename = f'{uuid.uuid4().hex[:10]}.{ext}'
    # user_id相当于user.id
    return f'user/photos/{instance.user_id}_{filename}'

# 在dango里面定义了一个数据库，数据库里面的一个数据就对应这个类的一个对象，类对应数据库里面的一个表
# 每个对象对应的信息有：user,photo,profile,create_time,update_time
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # default='user/photos/default.png'表示的路径默认相对在media文件夹下
    # upload_to表示上传路径
    photo=models.ImageField(default='user/photos/default.png', upload_to=photo_upload_to)
    # 简介
    profile=models.TextField(default='谢谢你的关注',max_length=500)
    # 创建时间
    create_time=models.DateTimeField(default=now)
    # 修改时间
    update_time=models.DateTimeField(default=now)
    def __str__(self):
        #定义的是在数据库看到的格式
        return f'{self.user.username} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}'