from django.urls import path
from mors_home import views

urlpatterns = [
    path('', views.search)
]