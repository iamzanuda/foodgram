from rest_framework.pagination import PageNumberPagination


class CustomLimitPaginanation(PageNumberPagination):
    page_size_query_param = 'limit'
