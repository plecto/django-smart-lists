from django.test import RequestFactory
from django.test import TestCase
from django.utils.safestring import SafeText
from django.views.generic import ListView

from smart_lists.exceptions import SmartListException
from smart_lists.filters import SmartListFilter
from smart_lists.helpers import SmartList, SmartOrder
from smart_lists.mixins import SmartListMixin
from testproject.models import SampleModel


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
