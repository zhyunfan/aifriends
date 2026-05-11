from django.urls import path

from web.views.index import index
from web.views.user.account.get_user_info import GetUserInfoView
from web.views.user.account.login import LoginView
from web.views.user.account.logout import LogoutView
from web.views.user.account.refresh_token import RefreshTokenView
from web.views.user.account.register import RegisterView

urlpatterns = [
    # 后端路由前面不加/，前端加/
    # path('user/account/login/',LoginView.as_view()),#如果改为前端格式那么就和前端冲突，打不开页面了
    path('api/user/account/login/',LoginView.as_view()),
    path('api/user/account/logout/',LogoutView.as_view()),
    path('api/user/account/register/',RegisterView.as_view()),
    path('api/user/account/refresh_token/',RefreshTokenView.as_view()),
    path('api/user/account/get_user_info/',GetUserInfoView.as_view()),
    path('',index)
]