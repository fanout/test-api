from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'messages/$', views.messages, name='messages'),
    url(r'messages/last/$', views.messages_last, name='messages_last'),
    url(r'messages/subscriptions/$', views.messages_subscriptions, name='messages_subscriptions'),
    url(r'messages/subscriptions/(?P<reg_id>[^/]+)/$', views.messages_subscriptions_item, name='messages_subscriptions_item'),
    url(r'send/$', views.send, name='send')
]
