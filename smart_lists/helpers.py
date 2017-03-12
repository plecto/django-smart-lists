import datetime

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Field
from django.utils.formats import localize
from django.utils.html import format_html
from django.utils.http import urlencode

from smart_lists.exceptions import SmartListException
from django.utils.translation import gettext_lazy as _



class TitleFromModelFieldMixin(object):
    def get_title(self):
        field = getattr(self.model, self.field_name)
        if self.model_field:
            return self.model_field.verbose_name.title()
        elif self.field_name == '__str__':
            return self.model._meta.verbose_name.title()
        elif callable(field) and getattr(field, 'short_description', False):
            return field.short_description
        return self.field_name.title()


class QueryParamsMixin(object):
    def get_url_with_query_params(self, new_query_dict):
        query = dict(self.query_params).copy()
        for key, value in query.items():
            if type(value) == list:
                query[key] = value[0]
        query.update(new_query_dict)
        for key, value in query.copy().items():
            if value is None:
                del query[key]
        return '?{}'.format(urlencode(query))


class SmartListField(object):
    def __init__(self, smart_list_item, column, object):
        self.smart_list_item = smart_list_item
        self.column = column
        self.object = object

    def get_value(self):
        field = getattr(self.object, self.column.field_name)
        if callable(field):
            if getattr(field, 'do_not_call_in_templates', False):
                return field
            else:
                return field()
        else:
            display_function = getattr(self.object, 'get_%s_display' % self.column.field_name, False)
            if display_function:
                return display_function()
            return field

    def format(self, value):
        if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
            return localize(value)
        return value

    def render(self):
        return format_html(
            '<td>{}</td>', self.format(self.get_value())
        )

    def render_link(self):
        if not hasattr(self.object, 'get_absolute_url'):
            raise SmartListException("Please make sure your model {} implements get_absolute_url()".format(type(self.object)))
        return format_html(
            '<td><a href="{}">{}</a></td>', self.object.get_absolute_url(), self.format(self.get_value())
        )


class SmartListItem(object):
    def __init__(self, smart_list, object):
        self.smart_list = smart_list
        self.object = object

    def fields(self):
        return [
            SmartListField(self, column, self.object) for column in self.smart_list.columns
        ]


class SmartOrder(QueryParamsMixin, object):
    def __init__(self, query_params, column_id, ordering_query_param):
        self.query_params = query_params
        self.column_id = column_id
        self.ordering_query_param = ordering_query_param
        self.query_order = query_params.get(ordering_query_param)
        self.current_columns = [int(col) for col in self.query_order.replace("-", "").split(".")] if self.query_order else []
        self.current_columns_length = len(self.current_columns)

    @property
    def priority(self):
        if self.is_ordered():
            return self.current_columns.index(self.column_id) + 1

    def is_ordered(self):
        return self.column_id in self.current_columns

    def is_reverse(self):
        for column in self.query_order.split('.'):
            c = column.replace("-", "")
            if int(c) == self.column_id:
                if column.startswith("-"):
                    return True
        return False

    def get_add_sort_by(self):
        if not self.is_ordered():
            if self.query_order:
                return self.get_url_with_query_params({
                    self.ordering_query_param: '{}.{}'.format(self.column_id, self.query_order)
                })
            else:
                return self.get_url_with_query_params({
                    self.ordering_query_param: self.column_id
                })
        elif self.current_columns_length > 1:
            new_query = []
            for column in self.query_order.split('.'):
                c = column.replace("-", "")
                if not int(c) == self.column_id:
                    new_query.append(column)
            if not self.is_reverse() and self.current_columns[0] == self.column_id:
                return self.get_url_with_query_params({
                    self.ordering_query_param: '-{}.{}'.format(self.column_id, ".".join(new_query))
                })
            else:
                return self.get_url_with_query_params({
                    self.ordering_query_param: '{}.{}'.format(self.column_id, ".".join(new_query))
                })

        else:
            return self.get_reverse_sort_by()

    def get_remove_sort_by(self):
        new_query = []
        for column in self.query_order.split('.'):
            c = column.replace("-", "")
            if not int(c) == self.column_id:
                new_query.append(column)
        return self.get_url_with_query_params({
            self.ordering_query_param: ".".join(new_query)
        })

    def get_reverse_sort_by(self):
        new_query = []
        for column in self.query_order.split('.'):
            c = column.replace("-", "")
            if int(c) == self.column_id:
                if column.startswith("-"):
                    new_query.append(c)
                else:
                    new_query.append('-{}'.format(c))
            else:
                new_query.append(column)

        return self.get_url_with_query_params({
            self.ordering_query_param: ".".join(new_query)
        })


class SmartColumn(TitleFromModelFieldMixin, object):
    def __init__(self, model, field, column_id, query_params, ordering_query_param):
        self.model = model
        self.field_name = field

        self.order_field = None
        if self.field_name.startswith("_") and self.field_name != "__str__":
            raise SmartListException("Cannot use underscore(_) variables/functions in smart lists")
        try:
            self.model_field = self.model._meta.get_field(self.field_name)
            self.order_field = self.field_name
        except FieldDoesNotExist:
            self.model_field = None
            field = getattr(self.model, self.field_name)
            if callable(field) and getattr(field, 'admin_order_field', False):
                self.order_field = getattr(field, 'admin_order_field')
            if callable(field) and getattr(field, 'alters_data', False):
                raise SmartListException("Cannot use a function that alters data in smart list")

        if self.order_field:
            self.order = SmartOrder(query_params=query_params, column_id=column_id, ordering_query_param=ordering_query_param)
        else:
            self.order = None


class SmartFilterValue(QueryParamsMixin, object):
    def __init__(self, field_name, label, value, query_params):
        self.field_name = field_name
        self.label = label
        self.value = value
        self.query_params = query_params

    def get_title(self):
        return self.label

    def get_url(self):
        return self.get_url_with_query_params({
            self.field_name: self.value
        })


class SmartFilter(TitleFromModelFieldMixin, object):
    def __init__(self, model, field, query_params):
        self.model = model
        self.field_name = field
        self.model_field = self.model._meta.get_field(self.field_name)
        self.query_params = query_params

    def get_values(self):
        if self.model_field.choices:
            return [SmartFilterValue(self.field_name, _("All"), None, self.query_params)] + [
                SmartFilterValue(self.field_name, choice[1], choice[0], self.query_params) for choice in self.model_field.choices
            ]


class SmartList(object):
    def __init__(self, object_list, list_settings):
        self.object_list = object_list
        self.model = object_list.model
        self.query_params = list_settings.get('query_params', {})
        self.list_display = list_settings.get('list_display')
        self.list_filter = list_settings.get('list_filter')
        self.ordering_query_value = list_settings.get('ordering_query_value', '')
        self.ordering_query_param = list_settings.get('ordering_query_param', 'o')
        self.columns = [
            SmartColumn(self.model, field, i, self.query_params, self.ordering_query_param) for i, field in enumerate(self.list_display, start=1)
        ] or [SmartColumn(self.model, '__str__', 1, self.ordering_query_value)]
        self.filters = [
            SmartFilter(self.model, field, self.query_params) for i, field in enumerate(self.list_filter, start=1)
        ] if self.list_filter else []


    @property
    def items(self):
        return [
            SmartListItem(self, obj) for obj in self.object_list
        ]