from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultSetPagination(PageNumberPagination):
    page_size_query_param = "size"
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('page', self.page.number),
            ('size', self.get_page_size(self.request)),
            ('num_pages', self.page.paginator.num_pages),
            ('results', data)
        ]))

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 123,
                },
                'page': {
                    'type': 'integer',
                    'example': 1,
                    'description': 'current page',
                    'nullable': False
                },
                'size': {
                    'type': 'integer',
                    'example': self.page_size,
                    'description': 'page size',
                    'nullable': False
                },
                'num_pages': {
                    'type': 'integer',
                    'example': 2,
                    'description': 'number of pages',
                    'nullable': False
                },
                'results': schema,
            },
        }
