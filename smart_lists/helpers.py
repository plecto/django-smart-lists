import datetime

from django.core.exceptions import FieldDoesNotExist
from django.db.models import BooleanField, ForeignKey
from django.utils.formats import localize
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.safestring import SafeText
from django.utils.translation import gettext_lazy as _
from typing import List
from typing import TYPE_CHECKING

from smart_lists.exceptions import SmartListException
from smart_lists.filters import SmartListFilter

if TYPE_CHECKING:
    from typing import Union, Tuple, Text, Callable, Optional


class TitleFromModelFieldMixin(object):
    def get_title(self):
        if getattr(self, 'label', None):
            return self.label
        elif self.model_field:
            return self.model_field.verbose_name.title()
        elif self.field_name == '__str__':
            return self.model._meta.verbose_name.title()
        try:
            field = getattr(self.model, self.field_name)
        except AttributeError as e:
            return self.field_name.title()
        if callable(field) and getattr(field, 'short_description', False):
            return field.short_description
        return self.field_name.replace("_", " ").title()


class QueryParamsMixin(object):
    def get_url_with_query_params(self, new_query_dict, without=None):
        without = without or []
        query = dict(self.query_params).copy()
        for key, value in query.items():
            if type(value) == list:
                query[key] = value[0]
            if key in without:
                query[key] = None
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
        if self.column.render_function:
            value = self.column.render_function(self.object)
            if not isinstance(value, SafeText):
                raise SmartListException(
                    'You need to provide instance of django.utils.safestring.SafeText not {}. Ensure that all user input was sanitized.'.format(
                        type(value)
                    )
                )
        elif isinstance(self.object, dict):
            value = self.object.get(self.column.field_name)
        else:
            field = getattr(self.object, self.column.field_name) if self.column.field_name else None
            if callable(field):
                value = field if getattr(field, 'do_not_call_in_templates', False) else field()
            else:
                display_function = getattr(self.object, 'get_%s_display' % self.column.field_name, False)
                value = display_function() if display_function else field

        return value

    def format(self, value):
        if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
            return localize(value)
        return value

    def render(self):
        return format_html('<td>{}</td>', self.format(self.get_value()))

    def render_link(self):
        if not self.has_link():
            raise SmartListException(
                "Please make sure your model {} implements get_absolute_url()".format(type(self.object))
            )
        return format_html('<td><a href="{}">{}</a></td>', self.get_absolute_url(), self.format(self.get_value()))

    def has_link(self):
        if self.object is None:
            return False
        if self.column.column_id == 1:
            obj = self.object
        else:
            obj = self.get_value()
        return hasattr(obj, 'get_absolute_url')

    def get_absolute_url(self):
        if self.column.column_id == 1:
            return self.object.get_absolute_url()
        return self.get_value().get_absolute_url()


class SmartListItem(object):
    def __init__(self, smart_list, object):
        self.smart_list = smart_list
        self.object = object

    def fields(self):
        return [SmartListField(self, column, self.object) for column in self.smart_list.columns]


class SmartOrder(QueryParamsMixin, object):
    def __init__(self, query_params, column_id, ordering_query_param):
        self.query_params = query_params
        self.column_id = column_id
        self.ordering_query_param = ordering_query_param
        self.query_order = query_params.get(ordering_query_param)
        self.current_columns = (
            [int(col) for col in self.query_order.replace("-", "").split(".")] if self.query_order else []
        )
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
                return self.get_url_with_query_params(
                    {self.ordering_query_param: '{}.{}'.format(self.column_id, self.query_order)}
                )
            else:
                return self.get_url_with_query_params({self.ordering_query_param: self.column_id})
        elif self.current_columns_length > 1:
            new_query = []
            for column in self.query_order.split('.'):
                c = column.replace("-", "")
                if not int(c) == self.column_id:
                    new_query.append(column)
            if not self.is_reverse() and self.current_columns[0] == self.column_id:
                return self.get_url_with_query_params(
                    {self.ordering_query_param: '-{}.{}'.format(self.column_id, ".".join(new_query))}
                )
            else:
                return self.get_url_with_query_params(
                    {self.ordering_query_param: '{}.{}'.format(self.column_id, ".".join(new_query))}
                )

        else:
            return self.get_reverse_sort_by()

    def get_remove_sort_by(self):
        new_query = []
        for column in self.query_order.split('.'):
            c = column.replace("-", "")
            if not int(c) == self.column_id:
                new_query.append(column)
        return self.get_url_with_query_params({self.ordering_query_param: ".".join(new_query)})

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

        return self.get_url_with_query_params({self.ordering_query_param: ".".join(new_query)})


class SmartColumn(TitleFromModelFieldMixin, object):
    def __init__(self, model, field, column_id, query_params, ordering_query_param, label=None, render_function=None):
        self.model = model
        self.field_name = field
        self.label = label
        self.render_function = render_function
        self.order_field = None
        self.order = None
        self.column_id = column_id

        # If there is no field_name that means it is not bound to any model field
        if not self.field_name:
            return

        if self.field_name.startswith("_") and self.field_name != "__str__":
            raise SmartListException("Cannot use underscore(_) variables/functions in smart lists")
        try:
            self.model_field = self.model._meta.get_field(self.field_name)
            self.order_field = self.field_name
        except FieldDoesNotExist:
            self.model_field = None
            try:
                field = getattr(self.model, self.field_name)
                if callable(field) and getattr(field, 'admin_order_field', False):
                    self.order_field = getattr(field, 'admin_order_field')
                if callable(field) and getattr(field, 'alters_data', False):
                    raise SmartListException("Cannot use a function that alters data in smart list")
            except AttributeError:
                self.order_field = self.field_name
                pass  # This is most likely a .values() query set

        if self.order_field:
            self.order = SmartOrder(
                query_params=query_params, column_id=column_id, ordering_query_param=ordering_query_param
            )


class SmartFilterValue(QueryParamsMixin, object):
    def __init__(self, field_name, label, value, query_params):
        self.field_name = field_name
        self.label = label
        self.value = value
        self.query_params = query_params

    def get_title(self):
        return self.label

    def get_url(self):
        # we are clearing pagination (`page` param) when setting new filter
        return self.get_url_with_query_params({self.field_name: self.value}, without=['page'])

    def is_active(self):
        if self.field_name in self.query_params:
            selected_value = self.query_params[self.field_name]
            if type(selected_value) == list:
                selected_value = selected_value[0]
            if selected_value == self.value:
                return True
        elif self.value is None:
            return True
        return False


class SmartFilter(TitleFromModelFieldMixin, object):
    def __init__(self, model, field, query_params, object_list, view):
        self.model = model

        if isinstance(field, SmartListFilter):
            self.field_name = field.parameter_name
            self.model_field = field
        else:
            self.field_name = field
            self.model_field = self.model._meta.get_field(self.field_name)
        self.query_params = query_params
        self.object_list = object_list
        self.view = view

    def get_title(self):
        if isinstance(self.model_field, SmartListFilter):
            return self.model_field.title
        return super(SmartFilter, self).get_title()

    def get_values(self):
        values = []
        if isinstance(self.model_field, SmartListFilter):
            values = [
                SmartFilterValue(self.model_field.parameter_name, choice[1], choice[0], self.query_params)
                for choice in self.model_field.lookups()
            ]
        elif self.model_field.choices:
            values = [
                SmartFilterValue(self.field_name, choice[1], choice[0], self.query_params)
                for choice in self.model_field.choices
            ]
        elif type(self.model_field) == BooleanField:
            values = [
                SmartFilterValue(self.field_name, choice[1], choice[0], self.query_params)
                for choice in ((1, _('Yes')), (0, _('No')))
            ]
        elif issubclass(type(self.model_field), ForeignKey):
            # use `self.view.object_list` in order to create filter from all objects not a paginated subset
            pks = self.view.object_list.order_by().distinct().values_list('%s__pk' % self.field_name, flat=True)
            remote_field = self.model_field.rel if hasattr(self.model_field, 'rel') else self.model_field.remote_field
            qs = remote_field.model.objects.filter(pk__in=pks)
            values = [SmartFilterValue(self.field_name, obj, str(obj.pk), self.query_params) for obj in qs]

        return [SmartFilterValue(self.field_name, _("All"), None, self.query_params)] + values


class SmartList(object):
    def __init__(
        self,
        object_list,
        query_params=None,
        list_display=None,
        list_filter=None,
        list_search=None,
        search_query_param=None,
        ordering_query_param=None,
        view=None,
    ):
        self.object_list = object_list
        self.model = object_list.model
        self.query_params = query_params or {}
        self.list_display = list_display or []
        self.list_filter = list_filter or []
        self.list_search = list_search or []
        self.search_query_value = self.query_params.get(search_query_param, '')
        self.search_query_param = search_query_param
        self.ordering_query_value = self.query_params.get(ordering_query_param, '')
        self.ordering_query_param = ordering_query_param

        self.columns = self.get_columns()

        self.filters = (
            [
                SmartFilter(self.model, field, self.query_params, self.object_list, view)
                for i, field in enumerate(self.list_filter, start=1)
            ]
            if self.list_filter
            else []
        )

    def get_columns(self):  # type: () -> List[SmartColumn]
        """
        Transform list_display into list of SmartColumns
        In list_display we expect:
         1. name of the field (string)
         or
         2. two element iterable in which:
            - first element is name of the field (string) or callable
              which returns html
            - label for the column (string)
        """

        if not self.list_display:
            return [SmartColumn(self.model, '__str__', 1, self.ordering_query_value, self.ordering_query_param)]

        columns = []
        for index, field in enumerate(self.list_display, start=1):
            kwargs = {
                'model': self.model,
                'column_id': index,
                'query_params': self.query_params,
                'ordering_query_param': self.ordering_query_param,
            }
            kwargs['field'], kwargs['render_function'], kwargs['label'] = normalize_list_display_item(field)
            columns.append(SmartColumn(**kwargs))
        return columns

    @property
    def items(self):
        return [SmartListItem(self, obj) for obj in self.object_list]


def normalize_list_display_item(
    field,
):  # type: (Union[Tuple[Callable, Text], Tuple[Text,Text], Text]) -> Tuple[Optional[Text], Optional[Callable], Optional[Text]]
    """
    We accept different types in list_display.
    This function handles them and transform into required format.
    """
    try:
        # Case with tuple with field_name and label
        if isinstance(field, str):
            # we want to avoid a situation where a string of length two (e.g. pk) will be unpacked
            raise ValueError
        field_name, label = field
        render_function = None
    except (TypeError, ValueError):
        # Case with only field_name
        field_name, render_function, label = field, None, None
    else:
        if callable(field_name):
            # Case with tuple with callable and label
            render_function, field_name = field_name, render_function
    return field_name, render_function, label


def render_column_template(template_name):
    from django.template.loader import get_template

    def func(obj):
        return get_template(template_name).render({'obj': obj})

    return func
