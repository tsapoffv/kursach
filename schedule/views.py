from django.http import JsonResponse, HttpResponseNotFound
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django import forms
from .models import Group, Teacher, Classroom, Subject, Lesson, DayOfWeek, WeekType, LessonType
from schedule.parser import parse_docx_file


def custom_404(request, exception):
    return render(request, 'schedule/404.html', status=404)

class GroupListView(ListView):
    """
    Отображает список всех учебных групп.
    """
    model = Group
    template_name = 'schedule/group_list.html'
    context_object_name = 'groups'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        groups = context['groups']
        
        courses = sorted(set(g.course for g in groups))
        groups_by_course = {}
        for course in courses:
            groups_by_course[course] = groups.filter(course=course)
        
        context['courses'] = courses
        context['groups_by_course'] = groups_by_course
        return context


def teacher_autocomplete(request):
    """
    API для автодополнения преподавателей.
    """
    query = request.GET.get('q', '')
    teachers = Teacher.objects.filter(
        Q(name__icontains=query)
    ).values_list('name', flat=True)[:10]
    return JsonResponse(list(teachers), safe=False)


def classroom_autocomplete(request):
    """
    API для автодополнения аудиторий.
    """
    query = request.GET.get('q', '')
    classrooms = Classroom.objects.filter(
        Q(name__icontains=query)
    ).values_list('name', flat=True)[:10]
    return JsonResponse(list(classrooms), safe=False)


class TeacherSearchView(DetailView):
    """
    Поиск преподавателя по имени и отображение его расписания.
    """
    model = Teacher
    template_name = 'schedule/filtered_schedule.html'
    pk_url_kwarg = 'teacher_pk'
    slug_url_kwarg = 'teacher_slug'
    context_object_name = 'teacher'

    def get_object(self):
        if hasattr(self, 'kwargs') and 'teacher_slug' in self.kwargs:
            slug = self.kwargs['teacher_slug']
            if slug:
                try:
                    return Teacher.objects.get(slug=slug)
                except Teacher.DoesNotExist:
                    return None
        
        name = self.request.GET.get('name', '').strip()
        if not name:
            return None
        try:
            return Teacher.objects.get(name__iexact=name)
        except Teacher.DoesNotExist:
            try:
                return Teacher.objects.filter(name__icontains=name).first()
            except Teacher.DoesNotExist:
                return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object:
            from django.shortcuts import render
            name = self.kwargs.get('teacher_slug', self.request.GET.get('name', ''))
            return render(request, 'schedule/404.html', {'name': name})
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lessons = self.object.lessons.values(
            'subject__name', 'time_slot', 'time_slot__name', 
            'day_id', 'week_type__code', 'lesson_type__code', 
            'classroom__name', 'classroom__slug',
            'teacher__name', 'teacher__slug',
            'denomination__name'
        ).distinct()
        context['title'] = f"Расписание преподавателя: {self.object.name}"
        context['schedule'] = self._organize_teacher_schedule(lessons)
        context['days_of_week'] = {d.number: d.name for d in DayOfWeek.objects.all()}
        context['lesson_type_map'] = {lt.code: lt.name for lt in LessonType.objects.all()}
        return context

    def _organize_teacher_schedule(self, lessons):
        days = {d.number: d for d in DayOfWeek.objects.all()}
        schedule = {day: {'A': [], 'B': []} for day in days}
        for lesson in lessons:
            week = lesson['week_type__code']
            if week in ['A', 'BOTH']:
                schedule[lesson['day_id']]['A'].append(lesson)
            if week in ['B', 'BOTH']:
                schedule[lesson['day_id']]['B'].append(lesson)
        return schedule

    def _organize_full_schedule(self, lessons):
        schedule = {day: {'A': [], 'B': []} for day, _ in Lesson.DAY_OF_WEEK_CHOICES}
        for lesson in lessons.order_by('start_time'):
            if lesson.week_type in ['A', 'BOTH']:
                schedule[lesson.day_of_week]['A'].append(lesson)
            if lesson.week_type in ['B', 'BOTH']:
                schedule[lesson.day_of_week]['B'].append(lesson)
        return schedule


class ClassroomSearchView(DetailView):
    """
    Поиск аудитории по номеру и отображение расписания.
    """
    model = Classroom
    template_name = 'schedule/filtered_schedule.html'
    pk_url_kwarg = 'classroom_pk'
    slug_url_kwarg = 'classroom_slug'
    context_object_name = 'classroom'

    def get_object(self):
        if hasattr(self, 'kwargs') and 'classroom_slug' in self.kwargs:
            slug = self.kwargs['classroom_slug']
            if slug:
                try:
                    return Classroom.objects.get(slug=slug)
                except Classroom.DoesNotExist:
                    return None
        
        name = self.request.GET.get('name', '').strip()
        if not name:
            return None
        try:
            return Classroom.objects.get(name__iexact=name)
        except Classroom.DoesNotExist:
            try:
                return Classroom.objects.filter(name__icontains=name).first()
            except Classroom.DoesNotExist:
                return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object:
            from django.shortcuts import render
            name = self.kwargs.get('classroom_slug', self.request.GET.get('name', ''))
            return render(request, 'schedule/404.html', {'name': name})
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lessons = self.object.lessons.values(
            'subject__name', 'time_slot', 'time_slot__name', 
            'day_id', 'week_type__code', 'lesson_type__code', 
            'classroom__name', 'classroom__slug',
            'teacher__name', 'teacher__slug',
            'denomination__name'
        ).distinct()
        context['title'] = f"Расписание аудитории: {self.object.name}"
        context['schedule'] = self._organize_teacher_schedule(lessons)
        context['days_of_week'] = {d.number: d.name for d in DayOfWeek.objects.all()}
        context['lesson_type_map'] = {lt.code: lt.name for lt in LessonType.objects.all()}
        return context

    def _organize_teacher_schedule(self, lessons):
        days = {d.number: d for d in DayOfWeek.objects.all()}
        schedule = {day: {'A': [], 'B': []} for day in days}
        for lesson in lessons:
            week = lesson['week_type__code']
            if week in ['A', 'BOTH']:
                schedule[lesson['day_id']]['A'].append(lesson)
            if week in ['B', 'BOTH']:
                schedule[lesson['day_id']]['B'].append(lesson)
        return schedule


class GroupScheduleView(DetailView):
    """
    Отображает расписание для конкретной группы, разделенное на две недели.
    """
    model = Group
    template_name = 'schedule/group_schedule.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()

        # Получаем и организуем занятия для каждой недели
        week_a_lessons = group.lessons.filter(week_type__code__in=['A', 'BOTH'])
        week_b_lessons = group.lessons.filter(week_type__code__in=['B', 'BOTH'])

        context['week_a_schedule'] = self._organize_schedule_by_day(week_a_lessons)
        context['week_b_schedule'] = self._organize_schedule_by_day(week_b_lessons)
        context['days_of_week'] = {d.number: d.name for d in DayOfWeek.objects.all()}
        return context

    def _organize_schedule_by_day(self, lessons):
        """ Группирует занятия по дням недели, объединяя одинаковые предметы. """
        from collections import defaultdict
        
        days_dict = {d.number: d for d in DayOfWeek.objects.all()}
        schedule = {day: [] for day in days_dict}
        
        # Группируем по (time_slot, subject, day) - объединяем одинаковые предметы
        grouped = defaultdict(list)
        for lesson in lessons.order_by('time_slot__start_time', 'subject__name', 'denomination__name'):
            key = (lesson.time_slot_id, lesson.subject_id, lesson.day_id, lesson.week_type_id)
            grouped[key].append(lesson)
        
        # Создаём структуру для шаблона
        for day in schedule:
            day_lessons = [lessons[0] for lessons in grouped.values() if lessons[0].day_id == day]
            # Добавляем все связанные занятия (подгруппы/группы) к каждому предмету
            for lesson in day_lessons:
                key = (lesson.time_slot_id, lesson.subject_id, lesson.day_id, lesson.week_type_id)
                lesson.related_lessons = grouped[key]
            schedule[day] = day_lessons
        
        return schedule


class FilteredScheduleView(DetailView):
    """
    Универсальное представление для отображения расписания, отфильтрованного
    по преподавателю, аудитории или предмету.
    """
    template_name = 'schedule/filtered_schedule.html'

    def get_queryset(self):
        # Определяем модель и имя pk в зависимости от URL
        if 'teacher_pk' in self.kwargs:
            self.model = Teacher
            self.pk_url_kwarg = 'teacher_pk'
        elif 'classroom_pk' in self.kwargs:
            self.model = Classroom
            self.pk_url_kwarg = 'classroom_pk'
        elif 'subject_pk' in self.kwargs:
            self.model = Subject
            self.pk_url_kwarg = 'subject_pk'
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.get_object()
        
        # Устанавливаем заголовок в зависимости от типа сущности
        if isinstance(entity, Teacher):
            context['title'] = f"Расписание преподавателя: {entity.name}"
        elif isinstance(entity, Classroom):
            context['title'] = f"Расписание аудитории: {entity.name}"
        elif isinstance(entity, Subject):
            context['title'] = f"Расписание по предмету: {entity.name}"

        # Получаем все занятия, связанные с этой сущностью
        lessons = entity.lessons.all()
        
        context['schedule'] = self._organize_full_schedule(lessons)
        context['days_of_week'] = dict(Lesson.DAY_OF_WEEK_CHOICES)
        return context

    def _organize_full_schedule(self, lessons):
        """ Группирует занятия по дням и неделям (A/B). """
        schedule = {day: {'A': [], 'B': []} for day, _ in Lesson.DAY_OF_WEEK_CHOICES}
        for lesson in lessons.order_by('start_time'):
            if lesson.week_type in ['A', 'BOTH']:
                schedule[lesson.day_of_week]['A'].append(lesson)
            if lesson.week_type in ['B', 'BOTH']:
                schedule[lesson.day_of_week]['B'].append(lesson)
        return schedule


class ImportForm(forms.Form):
    file = forms.FileField(label='Файл docx', widget=forms.ClearableFileInput(attrs={'accept': '.docx'}))
    clear = forms.BooleanField(label='Очистить расписание перед импортом', required=False)


@require_http_methods(["GET", "POST"])
def import_docx(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            doc_file = request.FILES['file']
            clear = form.cleaned_data.get('clear', False)

            try:
                import io
                result = parse_docx_file(io.BytesIO(doc_file.read()), clear=clear)
                return render(request, 'schedule/import.html', {
                    'form': ImportForm(),
                    'success': True,
                    'lessons_count': result['lessons'],
                    'errors': result['errors']
                })
            except Exception as e:
                import traceback
                traceback.print_exc()
                return render(request, 'schedule/import.html', {
                    'form': form,
                    'error': str(e)
                })
    else:
        form = ImportForm()

    return render(request, 'schedule/import.html', {'form': form})
