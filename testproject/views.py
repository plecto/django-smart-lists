from django.db.models import Q
from django.utils import timezone
from django.views.generic import ListView
from django.utils.safestring import SafeText

from smart_lists.exports import SmartListExcelExportBackend
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
    export_backends = [
        SmartListExcelExportBackend(
            verbose_name='Export blog posts to Excel', file_name='blog.xlsx', extra_filters=Q(category='blog_post')
        ),
        SmartListExcelExportBackend(verbose_name='Export to Excel (max. 5 rows)', file_name='small.xlsx', limit=5),
        SmartListExcelExportBackend(verbose_name='Export all to Excel', file_name='full.xlsx'),
    ]


class TestListView(SmartListMixin, ListView):
    model = SampleModel
    paginate_by = 100
    ordering_allowed_fields = ['title', 'category']
    list_display = ['title', 'category', 'foreign_1', 'foreign_2']
