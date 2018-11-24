from django.urls import path

from server.mors_seo import views

urlpatterns = [
    path('', views.UserListView.as_view()),
]