import six

from smart_lists.exceptions import SmartListException
from smart_lists.helpers import SmartColumn


class SmartListMixin(object):
    list_display = ()  # type: Tuple[str]
    list_filter = ()  # type: Tuple[str]
    search_fields = ()  # type: Tuple[str]
    date_hierarchy = ''

    ordering = []  # type: List[str]
    ordering_query_parameter_name = 'o'

    def get_queryset(self):
        qs = super(SmartListMixin, self).get_queryset()
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, six.string_types):
                ordering = (ordering,)
            qs = qs.order_by(*ordering)
        filters = self.get_filters()
        if filters:
            for fltr in filters:
                qs = qs.filter(**fltr)
        return qs

    def get_ordering(self):
        custom_order = self.request.GET.get(self.ordering_query_parameter_name)
        if custom_order:
            order_list = custom_order.split(".")
            ordering = []
            for i, order in enumerate(order_list, start=1):
                prefix = ''
                try:
                    if order.startswith("-"):
                        prefix = '-'
                        order = int(order[1:])
                    else:
                        order = int(order)
                    sc = SmartColumn(self.model, self.list_display[order-1], i, self.request.GET, self.ordering_query_parameter_name)
                    ordering.append(
                        '{}{}'.format(prefix, sc.order_field)
                    )
                except (ValueError, IndexError) as e:
                    raise SmartListException("Illegal ordering")
            return ordering
        return self.ordering

    def get_filters(self):
        flters = []
        for param, value in self.request.GET.items():
            if param in self.list_filter:
                flters.append({param: value})
        return flters

    def get_context_data(self, **kwargs):
        ctx = super(SmartListMixin, self).get_context_data(**kwargs)
        ctx.update({
            'smart_list_settings': {
                'list_display': self.list_display,
                'list_filter': self.list_filter,
                'ordering_query_value': self.request.GET.get(self.ordering_query_parameter_name, ''),
                'ordering_query_param': self.ordering_query_parameter_name,
                'query_params': self.request.GET
            }
        })
        return ctx
