import datetime

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Field
from django.utils.formats import localize
from django.utils.html import format_html

from smart_lists.exceptions import SmartListException


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


class SmartColumn(object):
    def __init__(self, model, field, column_order):
        self.model = model
        self.field_name = field
        self.column_order = column_order

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

    def get_title(self):
        if self.model_field:
            return self.model_field.verbose_name.title()
        if self.field_name == '__str__':
            return self.model._meta.verbose_name.title()
        return self.field_name.title()

    def get_query_order(self):
        return self.column_order if self.order_field else None

    def render(self):
        if self.order_field:
            return format_html('<th><a href="?o={order}">{label}</a></th>', order=self.get_query_order(),
                               label=self.get_title())
        else:
            return format_html('<th>{label}</th>', field_name=self.field_name, label=self.get_title())


class SmartList(object):
    def __init__(self, object_list, list_settings):
        self.object_list = object_list
        self.model = object_list.model
        self.list_display = list_settings.get('list_display')
        self.columns = [SmartColumn(self.model, field, i) for i, field in enumerate(self.list_display, start=1)] or [SmartColumn(self.model, '__str__', 1)]


    @property
    def items(self):
        return [
            SmartListItem(self, obj) for obj in self.object_list
        ]