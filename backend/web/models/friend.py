from django.db import models
from django.utils.timezone import now, localtime

from web.models.character import Character
from web.models.user import UserProfile


# 用户和每个虚拟角色的好友关系
class Friend(models.Model):
    me=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    character=models.ForeignKey(Character,on_delete=models.CASCADE)
    # 长期记忆
    memory=models.TextField(default='',max_length=5000,blank=True,null=True)
    create_time=models.DateTimeField(default=now)
    update_time=models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.character.name}-{self.me.user.username}-{localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"

class Message(models.Model):
    friend=models.ForeignKey(Friend,on_delete=models.CASCADE)
    user_message=models.TextField(max_length=500)
    input=models.TextField(max_length=10000)#输入会包含很多提示词
    output=models.TextField(max_length=500)
    # 输入Token:你发给 AI 的内容长度,输出 Token:AI 回复给你的内容长度
    input_tokens=models.IntegerField(default=0)
    output_tokens=models.IntegerField(default=0)
    total_tokens=models.IntegerField(default=0)
    create_time=models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.friend.character.name} - {self.friend.me.user.username}-{self.user_message[:50]}-{localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"

class SystemPrompt(models.Model):
    # 用来说明是什么模块（回复模块，记忆模块）
    # CharField只能一行，TextField能多行
    title=models.CharField(max_length=100)
    #定义一个顺序，因为一个模块可能提示词很长，要分块
    #会把同一个模块的提示词安装order_number排序拼接到一块
    order_number=models.IntegerField(default=0)
    prompt=models.TextField(max_length=10000)
    create_time=models.DateTimeField(default=now)
    update_time=models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.title}-{self.order_number}-{self.prompt[:50]}-{localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"








