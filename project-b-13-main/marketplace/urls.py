from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('categories/', views.category_list, name='category_list'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    path('create/', views.create_item, name='create_item'),
    path('my-items/', views.my_items, name='my_items'),
    path('item/<int:pk>/edit/', views.edit_item, name='edit_item'),
    path('item/<int:pk>/delete/', views.delete_item, name='delete_item'),
    path('transaction/initiate/<int:item_id>/', views.initiate_transaction, name='initiate_transaction'),
    path('transaction/complete/<int:transaction_id>/', views.complete_transaction, name='complete_transaction'),
    path('transaction/cancel/<int:transaction_id>/', views.cancel_transaction, name='cancel_transaction'),
    path('transaction/review/<int:transaction_id>/', views.leave_review, name='leave_review'),
    path('my-transactions/', views.my_transactions, name='my_transactions'),
    path('interests/', views.set_interests, name='set_interests'),
]