from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.test import TestCase
from django.views.generic import ListView

from smart_lists.exceptions import SmartListException
from smart_lists.helpers import SmartList, SmartOrder
from smart_lists.mixins import SmartListMixin
from testproject.models import SampleModel


class SmartListTestCase(TestCase):
    def setUp(self):
        self.sample = SampleModel.objects.create(
            title='I just love django-smart-lists!',
            category='blog_post'
        )
        self.factory = RequestFactory()

    def test_columns(self):
        smart_list = SmartList(
            SampleModel.objects.all(),
            list_settings={
                'list_display': ('title', 'category')
            }
        )

        self.assertEqual(len(smart_list.columns), 2)

    def test_illegal_method_list_display(self):
        self.assertRaises(
            SmartListException,
            SmartList,
            SampleModel.objects.all(),
            list_settings={
                'list_display': ('delete', )
            }
        )

        self.assertRaises(
            SmartListException,
            SmartList,
            SampleModel.objects.all(),
            list_settings={
                'list_display': ('_delete',)
            }
        )

    def test_ordering_of_columns(self):
        smart_list = SmartList(
            SampleModel.objects.all(),
            list_settings={
                'list_display': ('title', 'category', 'some_display_method', 'friendly_category')
            }
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
        self.assertRaises(
            SmartListException,
            view.get_ordering
        )

        request = self.factory.get('/smart-lists/?o=5')
        view = SampleModelListView(request=request)
        self.assertRaises(
            SmartListException,
            view.get_ordering
        )

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
        smart_list = SmartList(
            SampleModel.objects.all(),
            list_settings={
                'list_display': ('category',)
            }
        )
        self.assertEqual('Category', smart_list.columns[0].get_title())

    def test_get_column_from_method(self):
        smart_list = SmartList(
            SampleModel.objects.all(),
            list_settings={
                'list_display': ('some_display_method',)
            }
        )
        self.assertEqual('Some_Display_Method', smart_list.columns[0].get_title())

    def test_search(self):
        test = SampleModel.objects.create(title='test')
        foobar = SampleModel.objects.create(title='foobar')
        bar = SampleModel.objects.create(title='bar')

        class SampleModelListView(SmartListMixin, ListView):
            model = SampleModel
            list_display = ('title', 'category')
            search_fields = ('title', )

        request = self.factory.get('/smart-lists/?q=test')
        view = SampleModelListView(request=request)
        self.assertEqual(1, len(view.get_queryset()))
        self.assertEqual(test, view.get_queryset()[0])

        request = self.factory.get('/smart-lists/?q=bar')
        view = SampleModelListView(request=request)
        self.assertEqual(2, len(view.get_queryset()))
        self.assertEqual([foobar, bar], list(view.get_queryset()))
