import random
from django.core.management.base import BaseCommand
from schedule.models import Group, Teacher, Classroom, Subject, Lesson

# File for generating mockup date for database 

class Command(BaseCommand):
    help = 'Populates the database with dummy data for the schedule app'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate the database...'))

        # Clean up existing data to avoid duplicates
        Lesson.objects.all().delete()
        Group.objects.all().delete()
        Teacher.objects.all().delete()
        Classroom.objects.all().delete()
        Subject.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing schedule data.'))

        # --- Create Groups ---
        groups_data = ['IKBO-01-23', 'INBO-02-23', 'IT-15-23', 'IVBO-05-23']
        groups = [Group.objects.create(name=name) for name in groups_data]
        self.stdout.write(f'Created {len(groups)} groups.')

        # --- Create Teachers ---
        teachers_data = [
            'Dr. Ivan Ivanov', 'Prof. Maria Petrova', 'Dr. Alexey Sidorov',
            'Prof. Elena Smirnova', 'Dr. Dmitry Kuznetsov'
        ]
        teachers = [Teacher.objects.create(name=name) for name in teachers_data]
        self.stdout.write(f'Created {len(teachers)} teachers.')

        # --- Create Classrooms ---
        classrooms_data = ['101', '102-A', '205', '310-Lab', '404']
        classrooms = [Classroom.objects.create(name=name) for name in classrooms_data]
        self.stdout.write(f'Created {len(classrooms)} classrooms.')

        # --- Create Subjects ---
        subjects_data = [
            'Introduction to Python', 'Web Development with Django', 'Database Systems',
            'Algorithms and Data Structures', 'Software Engineering', 'Computer Networks'
        ]
        subjects = [Subject.objects.create(name=name) for name in subjects_data]
        self.stdout.write(f'Created {len(subjects)} subjects.')

        # --- Create Lessons ---
        lesson_times = ['09:00', '10:40', '12:20', '14:00', '15:40']
        week_types = ['A', 'B', 'BOTH']
        lesson_types = ['LEC', 'PRA', 'LAB']
        days_of_week = [1, 2, 3, 4, 5, 6]
        
        lessons_created = 0
        for group in groups:
            # Create a reasonable number of lessons per group
            for _ in range(random.randint(8, 15)):
                Lesson.objects.create(
                    group=group,
                    subject=random.choice(subjects),
                    teacher=random.choice(teachers),
                    classroom=random.choice(classrooms),
                    day_of_week=random.choice(days_of_week),
                    start_time=random.choice(lesson_times),
                    week_type=random.choice(week_types),
                    lesson_type=random.choice(lesson_types)
                )
                lessons_created += 1

        self.stdout.write(f'Created {lessons_created} lessons.')
        self.stdout.write(self.style.SUCCESS('Database successfully populated!'))
