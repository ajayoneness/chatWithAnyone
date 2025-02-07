from django.urls import path
from . import views

urlpatterns = [
    path('upload-chat/', views.UploadChatAPI.as_view()),
    path('chat/', views.ChatAPI.as_view()),
]