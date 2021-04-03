"""
Extend the LimitOffsetPagination class
"""

from rest_framework.pagination import LimitOffsetPagination


def _positive_int(integer_string, strict=False, cutoff=None):
    """
    Cast a string to a strictly positive integer.
    """
    ret = int(integer_string)
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        return min(ret, cutoff)
    return ret


class CustomPagination(LimitOffsetPagination):

    def get_limit(self, request):
        try:
            if request.query_params['limit'] == 'all':
                return None
        except:
            pass
        try:
            return _positive_int(
                request.query_params[self.limit_query_param],
                strict=True,
                cutoff=self.max_limit
            )
        except (KeyError, ValueError):
            pass

        return self.default_limit

    def paginate_queryset(self, queryset, request, view=None):
        self.count = self.get_count(queryset)
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        self.request = request
        if self.limit is None:
            self.limit = self.count
            return list(queryset)
        else:
            if self.count > self.limit and self.template is not None:
                self.display_page_controls = True
            if self.count == 0 or self.offset > self.count:
                return []
            return list(queryset[self.offset:self.offset + self.limit])
