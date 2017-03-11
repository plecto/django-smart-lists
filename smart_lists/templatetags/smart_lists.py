from django import template
from django.utils.safestring import mark_safe

from smart_lists.helpers import SmartList

register = template.Library()


@register.inclusion_tag("smart_lists/smart_list.html", takes_context=True)
def smart_list(context, object_list=None, page_obj=None, is_paginated=None, paginator=None):
    """
    Display the headers and data list together.

    TODO: Do pagination inside here??
    """
    if not object_list:
        object_list = context['object_list']
    if not page_obj:
        page_obj = context.get('page_obj', None)
    if not is_paginated:
        is_paginated = context.get('is_paginated')
    if not paginator:
        paginator = context.get('paginator')

    if 'smart_list_settings' not in context:
        raise Exception("Make sure you use the SmartListMixin and a ListView")

    smart_list_instance = SmartList(object_list, context['smart_list_settings'])
    return {'smart_list': smart_list_instance, 'page_obj': page_obj, 'is_paginated': is_paginated, 'paginator': paginator}
