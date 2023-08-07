from django.conf.urls import url
from send_mails import views



# app_name= "[UserAuthAndPermission]"
urlpatterns= [
    url(r'^get_result/', views.get_result),
]