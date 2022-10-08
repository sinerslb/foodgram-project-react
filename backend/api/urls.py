from django.urls import include, path
from django.conf.urls import url
from rest_framework import routers

# from api.views import PostViewSet

app_name = 'api'

router = routers.DefaultRouter()
# router.register(r'posts', PostViewSet)
# router.register(r'groups', GroupViewSet)
# router.register(
#     r'posts/(?P<post_id>\d+)/comments',
#     CommentsViewSet,
#     basename='comments'
# )
# router.register(r'follow', FollowViewSet, basename='follow')

urlpatterns = [
    url(r'^auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    # path('', include(router.urls)),
]
