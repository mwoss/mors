from django.urls import include, path
from rest_framework_jwt.views import refresh_jwt_token

urlpatterns = [
    path('auth/', include('rest_auth.urls')),
    path('auth/register/', include('rest_auth.registration.urls')),
    path('auth/refresh/', refresh_jwt_token),
    path('search', include('server.mors_home.urls')),
    path('seo/', include('server.mors_seo.urls')),
]
