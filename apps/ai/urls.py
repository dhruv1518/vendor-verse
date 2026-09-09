from django.urls import path
from . import views

app_name = "ai"

urlpatterns = [
    path("chat/", views.chat_message, name="chat_message"),
    path("status/", views.chat_status, name="chat_status"),
]
