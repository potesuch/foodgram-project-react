from rest_framework.pagination import PageNumberPagination


class LimitedPageNumberPagination(PageNumberPagination):
    """
    Кастомный пагинатор для ограниченного числа страниц.
    """
    page_size = 6
    page_size_query_param = 'limit'
