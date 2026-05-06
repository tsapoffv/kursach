from schedule.models import Teacher, Classroom
from django.utils.text import slugify
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Обновляет slug для преподавателей и аудиторий'

    def handle(self, *args, **options):
        count = 0
        for t in Teacher.objects.all():
            if not t.slug:
                t.slug = slugify(t.name) or None
                t.save()
                count += 1

        for c in Classroom.objects.all():
            if not c.slug:
                c.slug = slugify(c.name) or None
                c.save()
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Updated {count} objects'))