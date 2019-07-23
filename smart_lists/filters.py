class SmartListFilter(object):
    title = None
    parameter_name = None

    def __init__(self, request):
        self.request = request

    def value(self):
        return self.request.GET.get(self.parameter_name, None)

    def lookups(self):
        pass

    def queryset(self, queryset):
        pass
