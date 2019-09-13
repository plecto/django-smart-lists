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
    ordering_allowed_fields = ['title']
    list_display = (
        'title',
        'category',
        'some_display_method',
        (render_column_template('testproject/example_column_template.html'), 'Upper filter used for field'),
        (example_render_function, "Time"),
    )
    list_filter = ("category",)
