from django.db import models
from django.utils.translation import ugettext_lazy as _


CATEGORY_CHOICES = (('blog_post', _('Blog Post')), ('foo', _('Foo')), ('bar', _('Bar')))


class SampleModel(models.Model):
    title = models.CharField(max_length=128)
    category = models.CharField(max_length=128, choices=CATEGORY_CHOICES)

    def some_display_method(self):
        return "%s %s" % (self.title, self.category)

    def friendly_category(self):
        return self.get_category_display()

    friendly_category.admin_order_field = 'category'

    def _delete(self):
        self.delete()
