import datetime

import pytz
from openpyxl import load_workbook
from six import BytesIO

from django.test import RequestFactory
from django.test import TestCase
from django.utils.safestring import SafeText
from django.views.generic import ListView
from django.db.models import F, Q

from smart_lists.exceptions import SmartListException
from smart_lists.exports import SmartListExcelExportBackend, SmartListExportBackend
from smart_lists.filters import SmartListFilter
from smart_lists.helpers import SmartList, SmartOrder
from smart_lists.mixins import SmartListMixin
from testproject.models import SampleModel, ForeignModelWithUrl, ForeignModelWithoutUrl


class SmartListTestCase(TestCase):
    def setUp(self):
        self.sample = SampleModel.objects.create(title='I just love django-smart-lists!', category='blog_post')
        self.factory = RequestFactory()

    def test_columns(self):
        smart_list = SmartList(SampleModel.objects.all(), list_display=('title', 'category'))

        self.assertEqual(len(smart_list.columns), 2)

    def test_illegal_method_list_display(self):
        self.assertRaises(SmartListException, SmartList, SampleModel.objects.all(), list_display=('delete',))

        self.assertRaises(SmartListException, SmartList, SampleModel.objects.all(), list_display=('_delete',))

    def test_ordering_of_columns(self):
        smart_list = SmartList(
            SampleModel.objects.all(),
            **{'list_display': ('title', 'category', 'some_display_method', 'friendly_category')}
        )

        self.assertEqual(smart_list.columns[0].order_field, 'title')
        self.assertEqual(smart_list.columns[0].order.column_id, 1)
        self.assertEqual(smart_list.columns[1].order_field, 'category')
        self.assertEqual(smart_list.columns[1].order.column_id, 2)
        self.assertEqual(smart_list.columns[2].order_field, None)
        self.assertEqual(smart_list.columns[2].order, None)
        self.assertEqual(smart_list.columns[3].order_field, 'category')
        self.assertEqual(smart_list.columns[3].order.column_id, 4)

    def test_ordering_in_queryset(self):
        class SampleModelListView(SmartListMixin, ListView):
            model = SampleModel
            list_display = ('title', 'category')

        request = self.factory.get('/smart-lists/')
        view = SampleModelListView(request=request)
        self.assertEqual(view.get_ordering(), [])

        request = self.factory.get('/smart-lists/?o=1')
        view = SampleModelListView(request=request)
        self.assertEqual(view.get_ordering(), ['title'])

        request = self.factory.get('/smart-lists/?o=2.1')
        view = SampleModelListView(request=request)
        self.assertEqual(view.get_ordering(), ['category', 'title'])

        request = self.factory.get('/smart-lists/?o=-2.1')
        view = SampleModelListView(request=request)
        self.assertEqual(view.get_ordering(), ['-category', 'title'])

        request = self.factory.get('/smart-lists/?o=-wqdwd')
        view = SampleModelListView(request=request)
        self.assertRaises(SmartListException, view.get_ordering)

        request = self.factory.get('/smart-lists/?o=5')
        view = SampleModelListView(request=request)
        self.assertRaises(SmartListException, view.get_ordering)

    def test_smart_order(self):
        so = SmartOrder({'o': '1.2'}, 1, 'o')
        self.assertEqual(so.is_ordered(), True)
        self.assertEqual(so.is_reverse(), False)

        so = SmartOrder({'o': '-1.2'}, 1, 'o')
        self.assertEqual(so.is_ordered(), True)
        self.assertEqual(so.is_reverse(), True)

        so = SmartOrder({'o': '-1.2'}, 2, 'o')
        self.assertEqual(so.is_ordered(), True)
        self.assertEqual(so.is_reverse(), False)
        self.assertEqual(so.get_add_sort_by(), '?o=2.-1')

        so = SmartOrder({'o': '1'}, 1, 'o')
        self.assertEqual(so.is_ordered(), True)
        self.assertEqual(so.is_reverse(), False)
        self.assertEqual(so.get_add_sort_by(), '?o=-1')

    def test_get_verbose_column_title_with_fallback(self):
        smart_list = SmartList(SampleModel.objects.all(), **{'list_display': ('category',)})
        self.assertEqual('Category', smart_list.columns[0].get_title())

    def test_get_column_from_method(self):
        smart_list = SmartList(SampleModel.objects.all(), **{'list_display': ('some_display_method',)})
        self.assertEqual('Some Display Method', smart_list.columns[0].get_title())
        self.assertEqual('I just love django-smart-lists! blog_post', smart_list.items[0].fields()[0].get_value())

    def test_search(self):
        test = SampleModel.objects.create(title='test')
        foobar = SampleModel.objects.create(title='foobar')
        bar = SampleModel.objects.create(title='bar')

        class SampleModelListView(SmartListMixin, ListView):
            model = SampleModel
            list_display = ('title', 'category')
            search_fields = ('title',)

        request = self.factory.get('/smart-lists/?q=test')
        view = SampleModelListView(request=request)
        self.assertEqual(1, len(view.get_queryset()))
        self.assertEqual(test, view.get_queryset()[0])

        request = self.factory.get('/smart-lists/?q=bar')
        view = SampleModelListView(request=request)
        self.assertEqual(2, len(view.get_queryset()))
        self.assertEqual([foobar, bar], list(view.get_queryset()))

    def test_custom_filter_classes_parsing(self):
        class BlogOrNotFilter(SmartListFilter):
            parameter_name = 'blog'
            title = 'BlogOrNot'

            def lookups(self):
                return (('blog', 'Blog'), ('orNot', 'OR NOT!'))

            def queryset(self, queryset):
                if self.value() == 'blog':
                    return queryset.filter(category="blog_post")
                if self.value() == 'blog':
                    return queryset.exclude(category="blog_post")
                return queryset

        request = self.factory.get('/smart-lists/')
        smart_list = SmartList(
            SampleModel.objects.all(),
            list_display=('title', 'category'),
            list_filter=(BlogOrNotFilter(request), 'category'),
        )

        fltr = smart_list.filters[0]
        self.assertEqual(fltr.get_title(), 'BlogOrNot')

        values = fltr.get_values()
        self.assertEqual(values[0].get_title(), 'All')
        self.assertEqual(values[0].is_active(), True)
        self.assertEqual(values[1].get_title(), 'Blog')
        self.assertEqual(values[1].is_active(), False)
        self.assertEqual(values[2].get_title(), 'OR NOT!')
        self.assertEqual(values[2].is_active(), False)

        request = self.factory.get('/smart-lists/?blog=blog')
        smart_list = SmartList(
            SampleModel.objects.all(),
            list_display=('title', 'category'),
            list_filter=(BlogOrNotFilter(request),),
            query_params=request.GET,
        )

        fltr = smart_list.filters[0]
        values = fltr.get_values()
        self.assertEqual(values[0].is_active(), False)
        self.assertEqual(values[1].is_active(), True)
        self.assertEqual(values[2].is_active(), False)

    def test_custom_filter_classes_query(self):
        test = SampleModel.objects.create(title='test', category="blog_post")
        foo = SampleModel.objects.create(title='foo', category="foo")
        bar = SampleModel.objects.create(title='bar', category="bar")

        class BlogOrNotFilter(SmartListFilter):
            parameter_name = 'blog'
            title = 'BlogOrNot'

            def lookups(self):
                return (('blog', 'Blog'), ('orNot', 'OR NOT!'))

            def queryset(self, queryset):
                if self.value() == 'blog':
                    return queryset.filter(category="blog_post")
                if self.value() == 'blog':
                    return queryset.exclude(category="blog_post")
                return queryset

        class FakeView(SmartListMixin):
            list_filter = (BlogOrNotFilter, 'category')

        view = FakeView()

        request = self.factory.get('/smart-lists/')
        view.request = request
        self.assertEqual(view.smart_filter_queryset(SampleModel.objects.all()).count(), 4)  # init makes one as well

        request = self.factory.get('/smart-lists/?blog=blog')
        view.request = request
        self.assertEqual(view.smart_filter_queryset(SampleModel.objects.all()).count(), 2)  # init makes one as well

    def test_labels_for_columns(self):
        """Test if labels works properly."""
        label = 'Custom column label'
        smart_list = SmartList(SampleModel.objects.all(), list_display=('title', ('category', label)))

        column_with_custom_label = smart_list.columns[-1]

        self.assertEqual(label, column_with_custom_label.label)
        self.assertEqual(label, column_with_custom_label.get_title())

    def test_custom_html_column(self):
        """Test custom html column works properly."""
        render_column_function = lambda obj: SafeText('<b>Custom column redered</b>')
        smart_list = SmartList(
            SampleModel.objects.all(), list_display=('title', (render_column_function, 'Column label'))
        )

        smart_list_item_field_with_custom_render = smart_list.items[-1].fields()[-1].get_value()

        self.assertEqual(render_column_function(SampleModel.objects.last()), smart_list_item_field_with_custom_render)

    def test_has_link(self):
        foreign_1 = ForeignModelWithUrl.objects.create(title='foreign test')
        foreign_2 = ForeignModelWithoutUrl.objects.create(title='foreign test')
        SampleModel.objects.create(title='test', category="blog_post", foreign_1=foreign_1, foreign_2=foreign_2)
        SampleModel.objects.create(title='test', category="blog_post", foreign_1=None, foreign_2=None)

        smart_list = SmartList(SampleModel.objects.all(), list_display=('title', 'foreign_1', 'foreign_2'))
        # test if link exists
        test_1_item = smart_list.items[-2]
        self.assertTrue(test_1_item.fields()[0].has_link())
        self.assertEqual('/admin/testproject/samplemodel/2/change/', test_1_item.fields()[0].get_absolute_url())
        self.assertTrue(test_1_item.fields()[1].has_link())
        self.assertEqual('/admin/testproject/foreignmodelwithurl/1/change/', test_1_item.fields()[1].get_absolute_url())
        self.assertFalse(test_1_item.fields()[2].has_link())

        # test there is no link on None
        test_2_item = smart_list.items[-1]
        self.assertFalse(test_2_item.fields()[1].has_link())

    def test_new_filter_clears_pagination(self):
        request = self.factory.get('/smart-lists/?page=2&o=1&category=blog_post')
        smart_list = SmartList(
            SampleModel.objects.all(),
            list_display=('title', 'category'),
            list_filter=('title', 'category'),
            query_params=request.GET,
        )
        fltr = smart_list.filters[0]
        url = fltr.get_values()[0].get_url()
        self.assertEqual(set(url[1:].split('&')), set(['o=1', 'category=blog_post']))

    def test_queryset_returning_dict(self):
        qs = SampleModel.objects.all().annotate(custom=F('category')).values('custom', 'title')
        smart_list = SmartList(qs, list_display=('title', 'category'))

        self.assertEqual(
            'I just love django-smart-lists!',
            smart_list.items[0].fields()[0].get_value(),
        )

    def test_exporting_to_excel(self):
        SampleModel.objects.create(title='test', category='misc', some_date=datetime.date(2020, 1, 2))
        SampleModel.objects.create(
            title='retest', category='other', some_datetime=datetime.datetime(2020, 1, 2, 12, tzinfo=pytz.UTC)
        )
        SampleModel.objects.create(title='other')

        class SampleModelListView(SmartListMixin, ListView):
            model = SampleModel
            list_display = ('id', 'title', 'category', 'some_date', 'some_datetime')
            search_fields = ('title',)
            export_backends = [SmartListExcelExportBackend(verbose_name='Export to Excel', file_name='accounts.xlsx')]

        self.assertRedirects(
            SampleModelListView.as_view()(request=self.factory.get('/smart-lists/?q=test&e=1&o=1')),
            '/smart-lists/?q=test&o=1',
            fetch_redirect_response=False,
        )

        request = self.factory.get('/smart-lists/?q=test&e=0&o=1')
        response = SampleModelListView.as_view()(request=request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], SmartListExcelExportBackend.content_type)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=accounts.xlsx')
        wb = load_workbook(filename=BytesIO(response.content))
        data = [[cell.value for cell in row] for row in wb.active.rows]
        self.assertListEqual(
            data,
            [
                ['Id', 'Title', 'Category', 'Some Date', 'Some Datetime'],
                [2, 'test', 'misc', datetime.datetime(2020, 1, 2), 'None'],
                [3, 'retest', 'other', 'None', datetime.datetime(2020, 1, 2, 12)],
            ],
        )


class TestSmartListExportBackend(TestCase):
    class DummySmartListExportBackend(SmartListExportBackend):

        content_type = 'text/plain'

        def get_content(self, smart_list, value_renderer):
            rows = [';'.join(value_renderer(column.get_title()) for column in smart_list.get_columns())]
            for item in self.get_items(smart_list):
                rows.append(';'.join(value_renderer(field.get_value()) for field in item.fields()))
            return '\n'.join(rows).encode()

    def setUp(self):
        super(TestSmartListExportBackend, self).setUp()
        SampleModel.objects.create(title='First', category='blog_post')
        SampleModel.objects.create(title='Second', category='blog_post')
        self.smart_list = SmartList(SampleModel.objects.all(), list_display=('id', 'title', 'category'))

    def test_simple_export(self):
        backend = self.DummySmartListExportBackend(verbose_name='Test', file_name='test.csv')
        self.assertEqual(
            backend.get_content(self.smart_list, value_renderer=str).decode(),
            'Id;Title;Category\n1;First;Blog Post\n2;Second;Blog Post',
        )

    def test_extra_filters(self):
        backend = self.DummySmartListExportBackend(
            verbose_name='Test', file_name='first.csv', extra_filters=Q(title='First')
        )
        self.assertEqual(
            backend.get_content(self.smart_list, value_renderer=str).decode(), 'Id;Title;Category\n1;First;Blog Post'
        )

    def test_limit(self):
        backend = self.DummySmartListExportBackend(verbose_name='Test', file_name='first.csv', limit=1)
        self.assertEqual(
            backend.get_content(self.smart_list, value_renderer=str).decode(), 'Id;Title;Category\n1;First;Blog Post'
        )
