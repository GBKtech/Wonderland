from django.conf.urls import url
from main.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [

    url(r'^$', home, name='home'),
    url(r'^accounts/login/$', custom_login, name="login"),
    url(r'^signup/', signup, name='signup'),
    url(r'^accounts/logout/$', logout_page, name="logout"),
    url(r'^latest/$', latest, name='latest'),
    url(r'^trending/$', trending, name='trending'),
    url(r'^starredpost/$', myPinnedPost, name='myPinnedPost'),
    url(r'^mentions/$', MyMention, name='MyMention'),
    url(r'^(?P<slug>\w+)/comments', allMyComment, name='allmycomment'),
    url(r'^(?P<slug>\w+)/posts', allMyPost, name='allmypost'),
    url(r'^moderator/(?P<slug>\w+)$', moderator, name='moderator'),
    url(r'^EditProfile/(?P<slug>\w+)', EditProfile, name='EditProfile'),
    url(r'^editComment/(?P<pk>\d+)/update/$', CommentUpdate, name='comment_update'),
    url(r'^editPost/(?P<pk>\d+)/update/$', PostUpdate, name='post_update'),
    url(r'^accounts/activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        activate, name='activate'),
    url(r'^createComment/(?P<pk>\d+)/(?P<topic>[-\w]+)', createComment, name='comment'),
    url(r'^quoteComment/(?P<pk>\d+)/quote', quoteComment, name='quote'),
    url(r'^createTopic/(?P<section>\w+)', createTopic, name='createTopic'),
    url(r'^pinPost/', pin_post, name='pin_post'),
    url(r'^like/PostAction/', post_like, name='post_like'),
    url(r'^like/CommentAction/', comment_like, name='comment_like'),
    url(r'^post/ChangeStatus/', change_fp_mode, name='change_fp_mode'),
    url(r'^(?P<pk>\d+)/(?P<topic>[-\w]+)', page, name='post-detail'),
    url(r'^section/(?P<slug>[-\w]+)', section, name='section'),
    url(r'^popular/(?P<slug>[-\w]+)', popular, name='popular'),
    url(r'^(?P<slug>\w+)', userProfile, name='userProfile'), 
] 

# if settings.DEBUG:
#     urlpatterns += [
#         url(r'^media/(?P<path>.*)$', serve, {
#         'document_root': settings.MEDIA_ROOT,
#         }),
#     ]