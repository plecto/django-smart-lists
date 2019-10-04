from django.core.management import BaseCommand

from testproject.models import SampleModel, CATEGORY_CHOICES


class Command(BaseCommand):
    def handle(self, *args, **options):
        for i, (category, _) in enumerate(CATEGORY_CHOICES):
            for y in range(5):
                title = "Example title {}{}".format(i, y)
                SampleModel.objects.get_or_create(title=title, category=category)
        self.stdout.write("Example data created successfully.")
