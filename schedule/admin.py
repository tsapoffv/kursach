from django.contrib import admin
from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Group, Teacher, Classroom, Subject, Lesson
from .parser import parse_docx_file


class ImportForm(forms.Form):
    file = forms.FileField(label='Файл docx', widget=forms.ClearableFileInput(attrs={'accept': '.docx'}))
    clear = forms.BooleanField(label='Очистить расписание перед импортом', required=False)


class ScheduleAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['import_url'] = reverse('admin:schedule_lesson_import')
        return super().index(request, extra_context)

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        for app in app_list:
            app['import_url'] = reverse('admin:schedule_lesson_import')
        return app_list


schedule_site = ScheduleAdminSite(name='schedule_admin')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course')
    search_fields = ('name',)
    list_filter = ('course',)

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

    def get_urls(self):
        from django.urls import path
        return [
            path('import/', self.admin_site.admin_view(self.import_view), name='schedule_lesson_import'),
        ] + super().get_urls()

    def import_view(self, request):
        if request.method == 'POST':
            form = ImportForm(request.POST, request.FILES)
            if form.is_valid():
                doc_file = request.FILES['file']
                clear = form.cleaned_data.get('clear', False)
                import io
                result = parse_docx_file(io.BytesIO(doc_file.read()), clear=clear)
                self.message_user(request, f'Импортировано {result["lessons"]} занятий')
                return HttpResponseRedirect(request.path)
        else:
            form = ImportForm()
        
        return render(request, 'schedule/import_form.html', {
            'form': form,
            'title': 'Импорт расписания',
            'opts': self.opts,
        })

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        return list_display

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['import_url'] = 'import/'
        return super().changelist_view(request, extra_context)