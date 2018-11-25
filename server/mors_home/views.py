from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.request import Request

from aggregate_search import AggregateSearch
from search_engine.engine.engines.d2v_engine import D2VEngine
from search_engine.engine.engines.lda_engine import LdaEngine
from search_engine.engine.engines.tfidf_engine import TfidfEngine

aggregator = AggregateSearch(LdaEngine.from_configfile(), TfidfEngine.from_configfile(),
                             D2VEngine.from_configfile())


@api_view(['GET'])
@permission_classes((AllowAny, ))
def search(request: Request):
    query = request.query_params.get('query')
    limit = request.query_params.get('limit', 15) % 50
    return Response({
        "query": query,
        "result": aggregator.search(query)[:limit]
    })
