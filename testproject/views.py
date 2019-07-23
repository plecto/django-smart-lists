from django.views.generic import ListView

from smart_lists.mixins import SmartListMixin
from testproject.models import SampleModel


class TestListView(SmartListMixin, ListView):
    model = SampleModel
    paginate_by = 100
    ordering_allowed_fields = ['title', 'category']
    list_display = ['title', 'category', 'foreign_1', 'foreign_2']
