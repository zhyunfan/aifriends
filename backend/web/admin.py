from django.contrib import admin
from web.models.user import UserProfile

# 注解表示注册到admin里面
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    raw_id_fields=('user',)#逗号不要删，因为这里表示一个列表，如果没有逗号就一个元素就不是列表