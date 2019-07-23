from django.contrib import admin

from testproject.models import SampleModel, ForeignModelWithUrl, ForeignModelWithoutUrl

admin.site.register(SampleModel)
admin.site.register(ForeignModelWithUrl)
admin.site.register(ForeignModelWithoutUrl)
