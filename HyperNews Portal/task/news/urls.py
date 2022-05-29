from django.urls import path
from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('<int:news_id>/', views.NewsWithId.as_view(), name="news"),
    path('create/', views.CreateNewView.as_view(), name="create")
]
