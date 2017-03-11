import six


class SmartListMixin(object):
    list_display = ()  # type: Tuple[str]
    list_filter = ()  # type: Tuple[str]
    search_fields = ()  # type: Tuple[str]
    date_hierarchy = ''

    ordering = []  # type: List[str]
    ordering_allowed_fields = []  # type: List[str]

    def get_queryset(self):
        qs = super(SmartListMixin, self).get_queryset()
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, six.string_types):
                ordering = (ordering,)
            qs = qs.order_by(*ordering)
        return qs

    def get_ordering(self):
        custom_order = self.request.GET.get('order_by')
        if custom_order and custom_order in self.ordering_allowed_fields:
            return [custom_order]
        return self.ordering

    def get_context_data(self, **kwargs):
        ctx = super(SmartListMixin, self).get_context_data(**kwargs)
        ctx.update({
            'smart_list_settings': {
                'list_display': self.list_display,
                'list_filter': self.list_filter,
            }
        })
        return ctx
