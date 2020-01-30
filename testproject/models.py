from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


CATEGORY_CHOICES = (('blog_post', _('Blog Post')), ('foo', _('Foo')), ('bar', _('Bar')))


class ForeignModelWithUrl(models.Model):
    title = models.CharField(max_length=128)

    def get_absolute_url(self):
        return reverse(
            'admin:{app_label}_{model_name}_change'.format(
                app_label=self._meta.app_label, model_name=self._meta.model_name
            ),
            args=(self.id,),
        )

    def __str__(self):
        return self.title


class ForeignModelWithoutUrl(models.Model):
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title


class SampleModel(models.Model):
    title = models.CharField(max_length=128)
    category = models.CharField(max_length=128, choices=CATEGORY_CHOICES)
    foreign_1 = models.ForeignKey(ForeignModelWithUrl, on_delete=models.CASCADE, null=True, blank=True)
    foreign_2 = models.ForeignKey(ForeignModelWithoutUrl, on_delete=models.CASCADE, null=True, blank=True)

    def some_display_method(self):
        return "%s %s" % (self.title, self.category)

    def friendly_category(self):
        return self.get_category_display()

    friendly_category.admin_order_field = 'category'

    def _delete(self):
        self.delete()

    def get_absolute_url(self):
        return reverse(
            'admin:{app_label}_{model_name}_change'.format(
                app_label=self._meta.app_label, model_name=self._meta.model_name
            ),
            args=(self.id,),
        )
