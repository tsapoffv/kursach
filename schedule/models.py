from django.db import models
from slugify import slugify


class WeekType(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Код")
    name = models.CharField(max_length=50, verbose_name="Название")
    
    class Meta:
        verbose_name = "Тип недели"
        verbose_name_plural = "Типы недель"
    
    def __str__(self):
        return self.name


class LessonType(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Код")
    name = models.CharField(max_length=50, verbose_name="Название")
    
    class Meta:
        verbose_name = "Тип занятия"
        verbose_name_plural = "Типы занятий"
    
    def __str__(self):
        return self.name


class DayOfWeek(models.Model):
    number = models.IntegerField(unique=True, verbose_name="Номер")
    name = models.CharField(max_length=20, verbose_name="Название")
    
    class Meta:
        verbose_name = "День недели"
        verbose_name_plural = "Дни недели"
        ordering = ['number']
    
    def __str__(self):
        return self.name


class GroupDenominationType(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Код")
    name = models.CharField(max_length=50, verbose_name="Название")
    
    class Meta:
        verbose_name = "Тип группы"
        verbose_name_plural = "Типы групп"
    
    def __str__(self):
        return self.name


class GroupDenomination(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    type = models.ForeignKey(GroupDenominationType, on_delete=models.PROTECT, verbose_name="Тип")
    
    class Meta:
        verbose_name = "Вид группы"
        verbose_name_plural = "Виды групп"
    
    def __str__(self):
        return f"{self.name} ({self.type.name})"


class Group(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название группы")
    course = models.IntegerField(default=1, verbose_name="Курс")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
        ordering = ['course', 'name']
        constraints = [
            models.UniqueConstraint(fields=['name', 'course'], name='unique_group_per_course')
        ]

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания")

    class Meta:
        verbose_name = "Время занятия"
        verbose_name_plural = "Время занятий"
        ordering = ['start_time']

    def __str__(self):
        return f"{self.name} ({self.start_time}-{self.end_time})"


class Teacher(models.Model):
    name = models.CharField(max_length=200, verbose_name="ФИО преподавателя")
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            new_slug = slugify(self.name)
            if new_slug:
                self.slug = new_slug
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"

    def __str__(self):
        return self.name


class Classroom(models.Model):
    name = models.CharField(max_length=100, verbose_name="Номер аудитории")
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            new_slug = slugify(self.name)
            if new_slug:
                self.slug = new_slug
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Аудитория"
        verbose_name_plural = "Аудитории"

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название предмета")

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    def __str__(self):
        return self.name


class Lesson(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='lessons', verbose_name="Группа")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lessons', verbose_name="Предмет")
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons', verbose_name="Преподаватель")
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons', verbose_name="Аудитория")
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons', verbose_name="Время занятия")
    
    day = models.ForeignKey(DayOfWeek, on_delete=models.PROTECT, verbose_name="День недели", default=1)
    week_type = models.ForeignKey(WeekType, on_delete=models.PROTECT, verbose_name="Тип недели")
    lesson_type = models.ForeignKey(LessonType, on_delete=models.PROTECT, verbose_name="Тип занятия")
    denomination = models.ForeignKey(GroupDenomination, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons', verbose_name="Вид группы")
    
    start_time = models.TimeField(verbose_name="Время начала", blank=True, null=True)

    class Meta:
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"
        ordering = ['day__number', 'start_time']

    def __str__(self):
        return f"{self.subject} для {self.group} в {self.day.name} {self.start_time}"