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
{% load smart_lists %}

{% block content %}
    {% smart_list %}
{% endblock %}

```
