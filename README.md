# django-smart-lists

```python
from smart_lists.mixins import SmartListMixin

class AccountListView(LoginRequiredMixin, SmartListMixin, ListView):
    model = Account
    paginate_by = 100
    ordering_allowed_fields = ['company_name', 'code', 'created_date']
    list_display = ['company_name', 'code', 'created_date', 'balance']
```

This will give you a click-to-sort table with pagination. All you have to do is to make a template like this:

```html
{% extends "base.html" %}
{% load smart_list %}

{% block content %}
    {% smart_list %}
{% endblock %}
```
**The built-in templates are bootstrap 3 compatible - but override them easily (by positioning the apps in INSTALLED_APPS) to fit your own needs.
  When overriding the templates you may want to add extra context variables that will be passed through to your template.
  You can do it using the `extra` key in the context.**

## Other features

1. In case you need custom column name you can pass tuple with two strings.
   First string will indicate the name of the field second custom column label (see example below)
2. If you need column that is not bound to any model field then you can pass tuple with callable and string (column name).
   Callable need to take one argument (model object) and it must return instance of `django.utils.safestring.SafeString`
   Then it will be embedded into your smart list.
   
   You can use `render_column_template` helper which takes template name and render it with context that contains `obj` for you.
3. In order to allow for exporting your (possibly filtered) lists to downloadable files, define a list of `export_backends`.
   Currently we support only the Excel file format but feel free to create your own `smart_lists.exports.SmartListExportBackend`-based ones.

   You can define custom filtering for each export using the `extra_filters` argument.

   A limit of rows can be set using the `limit` argument. By default there is no limit.

Take a look at the example usage of advanced features.

```python
from smart_lists.exports import SmartListExcelExportBackend
from smart_lists.mixins import SmartListMixin
from smart_lists.helpers import render_column_template
from django.db.models import Q
from django.template.loader import get_template
from django.utils import timezone


def render_menu(obj):
    # Do sth with object
    context = {
        'obj': obj,
        'other_context': 'Lorem ipsum' * obj.count 
    }
    template = get_template('menu_template.hmtl')
    return template.render(context)
    

class AccountListView(LoginRequiredMixin, SmartListMixin, ListView):
    model = Account
    paginate_by = 100
    ordering_allowed_fields = ['company_name', 'code', 'created_date']
    list_display = [
        'company_name',
        'code',
        'created_date',
        ('balance', 'Custom Balance Label'), # Custom label
        (render_column_template('user_actions_template.html'), 'Actions') ,
        (render_menu, ''), # You can pass any callable
    ]
    export_backends = [
        SmartListExcelExportBackend(
            verbose_name='Export new to Excel',
            file_name='new.xlsx',
            extra_filters=lambda: Q(created_date__date__gte=timezone.now().date()),
        ),
        SmartListExcelExportBackend(verbose_name='Export to Excel (max. 5 rows)', file_name='small.xlsx', limit=5),
        SmartListExcelExportBackend(verbose_name='Export all to Excel', file_name='full.xlsx'),
    ]
```

## Development

### Setup

To set up the project locally run the below commands from the repository root:

```bash
$ python3 -m venv .venv  # if you're on Python 2 create virtualenv in another, appropriate way
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ pip install -r testproject/requirements.txt
$ ./manage.py test
$ ./manage.py migrate
$ ./manage.py seed_data  # this will create objects for list view
$ ./manage.py runserver  
```

Afterwards go to `http://localhost:8000` and see an example of smart list usage.

> NOTE: package versions in `requirements.txt` file are not pinned. If you wish to install specific versions
> you need to edit the file accordingly.

### Contributing 

To contribute to this project fork the repository and make a pull request against the `master` branch.

Remember to write tests for your changes!

## License

MIT License

Copyright (c) 2017 Plecto
