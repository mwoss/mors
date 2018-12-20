from django.urls import path
from server.mors_seo import views

urlpatterns = [
    path('optimization', views.seo_optimization),
    path('history/', views.seo_history_list_view)
]
