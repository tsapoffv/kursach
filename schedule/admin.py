from django.contrib import admin
from .models import Group, Teacher, Classroom, Subject, Lesson

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('subject', 'group', 'teacher', 'classroom', 'day_of_week', 'start_time', 'week_type')
    list_filter = ('group', 'teacher', 'classroom', 'day_of_week', 'week_type')
    search_fields = ('subject__name', 'teacher__name', 'group__name')
    autocomplete_fields = ['group', 'teacher', 'classroom', 'subject']