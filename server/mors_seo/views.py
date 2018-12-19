from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from seo.seo import SeoBooster
from server.mors_seo.models import User, SEOResult

seo = SeoBooster.from_configfile()

@api_view(['GET'])
def seo_history_list_view(request: Request):
    pass

@api_view(['POST'])
def seo_optimization(request: Request):
    text_area = request.data['textArea']
    query = request.data['query']

    seo_result = {
        "score": seo.compute_similarity(text_area, query),
        "query_keywords": seo.compute_keywords(query),
        "document_keywords": seo.compute_keywords(text_area),
        "general": seo.words_to_add_simple(text_area, query),
        "specific": seo.words_to_add_full(text_area, query),
    }

    user = User.objects.get(email=request.user.email)
    user.seo_result.append(SEOResult(**seo_result))
    user.save()

    return Response(seo_result)
