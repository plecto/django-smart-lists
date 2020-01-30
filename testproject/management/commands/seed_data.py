from django.core.management import BaseCommand

from testproject.models import (
    CATEGORY_CHOICES,
    SampleModel,
    ForeignModelWithoutUrl,
    ForeignModelWithUrl,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for i, (category, _) in enumerate(CATEGORY_CHOICES):
            for y in range(5):
                title = "Example title {}{}".format(i, y)
                f1_title = "ForeignModelWithUrl title {}{}".format(i, y)
                f2_title = "ForeignModelWithoutUrl title {}{}".format(i, y)
                f1, _ = ForeignModelWithUrl.objects.get_or_create(title=f1_title)
                f2, _ = ForeignModelWithoutUrl.objects.get_or_create(title=f2_title)
                SampleModel.objects.get_or_create(title=title, category=category, foreign_1=f1, foreign_2=f2)
        self.stdout.write("Example data created successfully.")
