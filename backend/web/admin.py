from django.contrib import admin
from web.models.user import UserProfile
from web.models.character import Character

# 注解表示注册到admin里面
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # user是外键
    raw_id_fields=('user',)#逗号不要删，因为这里表示一个列表，如果没有逗号就一个元素就不是列表

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    raw_id_fields = ('author',)