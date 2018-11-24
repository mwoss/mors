from rest_framework import generics
from rest_framework.permissions import AllowAny

from server.mors_seo import models
from server.mors_seo import serializers


class UserListView(generics.ListCreateAPIView):
    permission_classes = (AllowAny, )
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
