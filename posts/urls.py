from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('create/', views.post_create, name='create'),
    path('<int:pk>/', views.post_detail, name='detail'),
    path('<int:pk>/delete/', views.post_delete, name='delete'),
    path('<int:pk>/like/', views.like_toggle, name='like'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path('explore/', views.explore_view, name='explore'),
]
