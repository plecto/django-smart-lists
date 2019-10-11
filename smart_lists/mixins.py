import operator
from functools import reduce

import six
from django.db.models import Q
from typing import TYPE_CHECKING

from smart_lists.exceptions import SmartListException
from smart_lists.filters import SmartListFilter
from smart_lists.helpers import SmartColumn, normalize_list_display_item

if TYPE_CHECKING:
    from typing import Tuple, List


class SmartListMixin(object):
    list_display = ()  # type: Tuple[str]
    list_filter = ()  # type: Tuple[str]
    search_fields = ()  # type: Tuple[str]
    date_hierarchy = ''

    ordering = []  # type: List[str]
    ordering_query_parameter_name = 'o'
    search_query_parameter_name = 'q'

    def get_queryset(self):
        qs = super(SmartListMixin, self).get_queryset()
        return self.smart_filter_queryset(qs)

    def smart_filter_queryset(self, qs):
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, six.string_types):
                ordering = (ordering,)
            qs = qs.order_by(*ordering)
        qs = self.apply_filters(qs)
        search_filters = self.get_search_filters()
        if search_filters:
            for fltr in search_filters:
                qs = qs.filter(fltr)
        return qs

    def get_search_filters(self):
        """
        borrowed from django-admin
        @return: list of search filters
        """
        search_term = self.request.GET.get(self.search_query_parameter_name, '')
        if len(search_term) >= 0:

            def construct_search(field_name):
                if field_name.startswith('^'):
                    return "%s__istartswith" % field_name[1:]
                elif field_name.startswith('='):
                    return "%s__iexact" % field_name[1:]
                elif field_name.startswith('@'):
                    return "%s__search" % field_name[1:]
                else:
                    return "%s__icontains" % field_name

            search_filters = []
            if self.search_fields and search_term:
                orm_lookups = [construct_search(str(search_field)) for search_field in self.search_fields]
                search_filters = []
                for bit in search_term.split():
                    or_queries = [Q(**{orm_lookup: bit}) for orm_lookup in orm_lookups]
                    search_filters.append(reduce(operator.or_, or_queries))
            return search_filters

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
                    field_name, render_function, label = normalize_list_display_item(self.list_display[order - 1])
                    sc = SmartColumn(
                        model=self.model,
                        field=field_name,
                        column_id=i,
                        query_params=self.request.GET,
                        ordering_query_param=self.ordering_query_parameter_name,
                        label=label,
                        render_function=render_function,
                    )
                    ordering.append('{}{}'.format(prefix, sc.order_field))
                except (ValueError, IndexError) as e:
                    raise SmartListException("Illegal ordering")
            return ordering
        return self.ordering

    def apply_filters(self, qs):
        for fltr in self.list_filter:
            parameter_name = fltr
            if type(fltr) != str and issubclass(fltr, SmartListFilter):
                qs = fltr(self.request).queryset(qs)
            else:
                if parameter_name in self.request.GET:
                    qs = qs.filter(**{parameter_name: self.request.GET[parameter_name]})
        return qs

    def get_list_display(self):
        return list(self.list_display)

    def get_context_data(self, **kwargs):
        ctx = super(SmartListMixin, self).get_context_data(**kwargs)
        ctx.update(
            {
                'smart_list_settings': {
                    'list_display': self.get_list_display(),
                    'list_filter': [
                        fltr(self.request) if not isinstance(fltr, str) and issubclass(fltr, SmartListFilter) else fltr
                        for fltr in self.list_filter
                    ],
                    'list_search': self.search_fields,
                    'ordering_query_param': self.ordering_query_parameter_name,
                    'search_query_param': self.search_query_parameter_name,
                    'query_params': self.request.GET,
                }
            }
        )
        return ctx
