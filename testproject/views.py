from django.utils import timezone
from django.views.generic import ListView
from django.utils.safestring import SafeText

from smart_lists.helpers import render_column_template
from smart_lists.mixins import SmartListMixin

from testproject.models import SampleModel


def example_render_function(obj):
    return SafeText(timezone.now())


class SampleModelListView(SmartListMixin, ListView):
    model = SampleModel
    paginate_by = 5
    ordering = ['category']
    ordering_allowed_fields = ['title']
    list_display = (
        'title',
        'foreign_1',
        'category',
        'some_display_method',
        (render_column_template('testproject/example_column_template.html'), 'Upper filter used for field'),
        (example_render_function, "Time"),
    )
    list_filter = ("category", 'foreign_1')


class TestListView(SmartListMixin, ListView):
    model = SampleModel
    paginate_by = 100
    ordering_allowed_fields = ['title', 'category']
    list_display = ['title', 'category', 'foreign_1', 'foreign_2']
