from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('new/', views.new_conversation, name='new'),
    path('<int:convo_id>/', views.conversation_detail, name='detail'),
]