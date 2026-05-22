from django.urls import path, re_path

from web.views.create.character.create import CreateCharacterView
from web.views.create.character.get_list import GetListCharacterView
from web.views.create.character.get_single import GetSingleCharacterView
from web.views.create.character.remove import RemoveCharacterView
from web.views.create.character.update import UpdateCharacterView
from web.views.friend.get_list import GetListFriendView
from web.views.friend.get_or_create import GetOrCreateFriendView
from web.views.friend.message.chat.chat import MessageChatView
from web.views.friend.message.get_history import GetHistoryView
from web.views.friend.remove import RemoveFriendView
from web.views.homepage.index import HomepageIndexView
from web.views.index import index
from web.views.user.account.get_user_info import GetUserInfoView
from web.views.user.account.login import LoginView
from web.views.user.account.logout import LogoutView
from web.views.user.account.refresh_token import RefreshTokenView
from web.views.user.account.register import RegisterView
from web.views.user.profile.update import UpdateProfileView

urlpatterns = [
    # 后端路由前面不加/，前端加/
    # path('user/account/login/',LoginView.as_view()),#如果改为前端格式那么就和前端冲突，打不开页面了
    path('api/user/account/login/',LoginView.as_view()),
    path('api/user/account/logout/',LogoutView.as_view()),
    path('api/user/account/register/',RegisterView.as_view()),
    path('api/user/account/refresh_token/',RefreshTokenView.as_view()),
    path('api/user/account/get_user_info/',GetUserInfoView.as_view()),
    path('api/user/profile/update/',UpdateProfileView.as_view()),
    path('api/create/character/create/',CreateCharacterView.as_view()),
    path('api/create/character/update/',UpdateCharacterView.as_view()),
    path('api/create/character/remove/',RemoveCharacterView.as_view()),
    path('api/create/character/get_single/',GetSingleCharacterView.as_view()),
    path('api/create/character/get_list/',GetListCharacterView.as_view()),
    path('api/homepage/index',HomepageIndexView.as_view()),
    path('api/friend/get_or_create/',GetOrCreateFriendView.as_view()),
    path('api/friend/remove/',RemoveFriendView.as_view()),
    path('api/friend/get_list/',GetListFriendView.as_view()),
    path('api/friend/message/chat',MessageChatView.as_view()),
    path('api/friend/message/get_history',GetHistoryView.as_view()),
    path('',index),
    #ctrl+点击index跳转到index.py对应index.html即前端页面，再根据前端设置的路径跳到对应页面（前端页面的RouterView->router/index.js）就不会出现比如用户登录后点击创作
    # 即http://127.0.0.1:8000/create/不会出现页面找不到
    re_path(r'^(?!media/|static/|assets/).*$', index)#匹配所有不以静态文件开头的路由
]