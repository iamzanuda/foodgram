from rest_framework.pagination import PageNumberPagination


class CastomLimitPaginanation(PageNumberPagination):
    page_size_query_param = 'limit'
