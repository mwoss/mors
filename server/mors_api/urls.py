from django.urls import include, path
from rest_framework.schemas import get_schema_view

urlpatterns = [
    path('', get_schema_view()),
    path('auth/', include('rest_auth.urls')),
    path('auth/register/', include('rest_auth.registration.urls')),
    path('search', include('server.mors_home.urls')),
    path('seo/', include('server.mors_seo.urls')),
]
