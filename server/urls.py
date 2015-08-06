from django.conf.urls import include, url

urlpatterns = [
    url(r'', include('test_api.urls')),
]
