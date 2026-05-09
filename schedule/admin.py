from django.contrib import admin
from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Group, Teacher, Classroom, Subject, Lesson
from .parser import parse_docx_file


class ImportForm(forms.Form):
    file = forms.FileField(label='Файл docx', widget=forms.ClearableFileInput(attrs={'accept': '.docx'}))
    clear = forms.BooleanField(label='Очистить занятия группы перед импортом', required=False)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course')
    search_fields = ('name',)
    list_filter = ('course',)
    change_list_template = 'admin/schedule/group_list.html'

    def get_urls(self):
        from django.urls import path
        return [
            path('import/', self.admin_site.admin_view(self.import_view), name='schedule_group_import'),
        ] + super().get_urls()

    def import_view(self, request):
        if request.method == 'POST':
            form = ImportForm(request.POST, request.FILES)
            if form.is_valid():
                doc_file = request.FILES['file']
                clear = form.cleaned_data.get('clear', False)
                import io
                result = parse_docx_file(io.BytesIO(doc_file.read()), clear=clear)
                if result['errors']:
                    for error in result['errors']:
                        self.message_user(request, error, level='ERROR')
                self.message_user(request, f'Импортировано {result["lessons"]} занятий')
                return HttpResponseRedirect(request.path)
        else:
            form = ImportForm()
        
        return render(request, 'schedule/import_form.html', {
            'form': form,
            'title': 'Импорт расписания',
            'opts': self.opts,
        })

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
    list_display = ('subject', 'group', 'teacher', 'classroom', 'day_of_week', 'start_time', 'week_type', 'subgroup')
    list_filter = ('group', 'teacher', 'classroom', 'day_of_week', 'week_type', 'subgroup')
    search_fields = ('subject__name', 'teacher__name', 'group__name')
    autocomplete_fields = ['group', 'teacher', 'classroom', 'subject']