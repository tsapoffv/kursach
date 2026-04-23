from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название группы")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

class Teacher(models.Model):
    name = models.CharField(max_length=200, verbose_name="ФИО преподавателя")
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"

class Classroom(models.Model):
    name = models.CharField(max_length=100, verbose_name="Номер аудитории")
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Аудитория"
        verbose_name_plural = "Аудитории"

class Subject(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название предмета")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

class Lesson(models.Model):
    WEEK_TYPE_CHOICES = [
        ('A', 'Неделя А (четн.)'),
        ('B', 'Неделя Б (неч.)'),
        ('BOTH', 'Обе недели'),
    ]
    
    LESSON_TYPE_CHOICES = [
        ('LEC', 'Лекция'),
        ('PRA', 'Практика'),
        ('LAB', 'Лабораторная'),
    ]

    DAY_OF_WEEK_CHOICES = [
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='lessons', verbose_name="Группа")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lessons', verbose_name="Предмет")
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons', verbose_name="Преподаватель")
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons', verbose_name="Аудитория")
    
    day_of_week = models.IntegerField(choices=DAY_OF_WEEK_CHOICES, verbose_name="День недели")
    start_time = models.TimeField(verbose_name="Время начала")
    
    week_type = models.CharField(max_length=4, choices=WEEK_TYPE_CHOICES, verbose_name="Тип недели")
    lesson_type = models.CharField(max_length=3, choices=LESSON_TYPE_CHOICES, verbose_name="Тип занятия")

    def __str__(self):
        return f"{self.subject} для {self.group} в {self.get_day_of_week_display()} {self.start_time}"

    class Meta:
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"
        ordering = ['day_of_week', 'start_time']