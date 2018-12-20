from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request

from aggregate_search import AggregateSearch
from search_engine.engine.engines.d2v_engine import D2VEngine
from search_engine.engine.engines.lda_engine import LdaEngine
from search_engine.engine.engines.tfidf_engine import TfidfEngine

from server.mors_home.model import Site

# aggregator = AggregateSearch(LdaEngine.from_configfile(), TfidfEngine.from_configfile(),
#                              D2VEngine.from_configfile())


@api_view(['GET'])
@permission_classes((AllowAny,))
def search(request: Request):
    pass
    # query = request.query_params.get('query')
    # limit = request.query_params.get('limit', 15) % 50
    # result = aggregator.search(query)[:limit]
    #
    # return Response({
    #     "query": query,
    #     "result": [url_d for url_d in Site.objects.mongo_find({
    #         'url': {
    #             '$in': [r[0] for r in result]
    #         }
    #     }, {'url': 1, 'tittle': 1, 'description': 1, '_id': 0})]
    # })
