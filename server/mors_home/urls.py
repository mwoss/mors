from django.urls import path
from server.mors_home import views

urlpatterns = [
    path('', views.search)
]