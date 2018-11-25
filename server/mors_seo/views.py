from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from server.mors_seo import models
from server.mors_seo import serializers


class UserListView(generics.ListCreateAPIView):
    permission_classes = (AllowAny, )
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


@api_view(['POST'])
def seoOptimization(request: Request):
    textName = request.query_params.get('textName')
    query = request.query_params.get('query')
    textArea = request.query_params.get('textArea')

    return Response({
        "score": '90',
    })