from django.urls import path
from server.mors_seo import views

urlpatterns = [
    path('optimization', views.seoOptimization),
]
