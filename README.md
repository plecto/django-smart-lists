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
**The built-in templates are bootstrap 3 compatible - but override them easily (by positioning the apps in INSTALLED_APPS) to fit your own needs**

# Other features

django-smart-lists supports commmon method attributes supported by django admin, such as:

```python

class EpicModel(models.Model):
    title = models.CharField(max_length=128)
    
    def get_pretty_title(self):
        return "Pretty {}".format(self.title)
    get_pretty_title.short_description = 'Pretty Title'
    get_pretty_title.admin_order_field = 'title'
    

### License

MIT License

Copyright (c) 2017 Plecto
