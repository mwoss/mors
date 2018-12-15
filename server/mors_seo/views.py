from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from seo.seo import SeoBooster
from server.mors_seo import models
from server.mors_seo import serializers

seo = SeoBooster.from_configfile()


class UserListView(generics.ListCreateAPIView):
    permission_classes = (AllowAny, )
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


@api_view(['POST'])
def seoOptimization(request: Request):
    data =request.data
    textArea = data['textArea']
    textName = data['textName']
    query = data['query']

    # TODO tutaj sa te rzeczy które trzeba wstwić do bazy
    score = seo.compute_similarity(textArea, query),
    queryKeywords = seo.compute_keywords(query),
    documentKeywords = seo.compute_keywords(textArea),
    general = seo.words_to_add_simple(textArea, query),
    specific = seo.words_to_add_full(textArea, query),
    flipSuggestions = {}

    return Response({
        "score": score,
        "queryKeywords": queryKeywords,
        "documentKeywords": documentKeywords,
        "general": general,
        "specific": specific,
        "flipSuggestions": temporaryFlipSuggestions()
    })

def temporaryFlipSuggestions():
     my_dict = {'priest': 'pope',
               'children':'child',
               'kufer':'skrzynia'}
     return  my_dict
