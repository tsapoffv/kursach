from django.http import JsonResponse, HttpResponseNotFound
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.shortcuts import render
from .models import Group, Teacher, Classroom, Subject, Lesson


def custom_404(request, exception):
    return render(request, 'schedule/404.html', status=404)

class GroupListView(ListView):
    """
    Отображает список всех учебных групп.
    """
    model = Group
    template_name = 'schedule/group_list.html'
    context_object_name = 'groups'


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
        # Checking is the a parameter in URL
        if hasattr(self, 'kwargs') and 'teacher_slug' in self.kwargs:
            slug = self.kwargs['teacher_slug']
            try:
                return Teacher.objects.get(slug=slug)
            except Teacher.DoesNotExist:
                return None
        
        # Or searching by get parameter
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
        lessons = self.object.lessons.all()
        context['title'] = f"Расписание преподавателя: {self.object.name}"
        context['schedule'] = self._organize_full_schedule(lessons)
        context['days_of_week'] = dict(Lesson.DAY_OF_WEEK_CHOICES)
        return context

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
        lessons = self.object.lessons.all()
        context['title'] = f"Расписание аудитории: {self.object.name}"
        context['schedule'] = self._organize_full_schedule(lessons)
        context['days_of_week'] = dict(Lesson.DAY_OF_WEEK_CHOICES)
        return context

    def _organize_full_schedule(self, lessons):
        schedule = {day: {'A': [], 'B': []} for day, _ in Lesson.DAY_OF_WEEK_CHOICES}
        for lesson in lessons.order_by('start_time'):
            if lesson.week_type in ['A', 'BOTH']:
                schedule[lesson.day_of_week]['A'].append(lesson)
            if lesson.week_type in ['B', 'BOTH']:
                schedule[lesson.day_of_week]['B'].append(lesson)
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
        week_a_lessons = group.lessons.filter(week_type__in=['A', 'BOTH'])
        week_b_lessons = group.lessons.filter(week_type__in=['B', 'BOTH'])

        context['week_a_schedule'] = self._organize_schedule_by_day(week_a_lessons)
        context['week_b_schedule'] = self._organize_schedule_by_day(week_b_lessons)
        context['days_of_week'] = dict(Lesson.DAY_OF_WEEK_CHOICES)
        return context

    def _organize_schedule_by_day(self, lessons):
        """ Группирует занятия по дням недели. """
        schedule = {day: [] for day, _ in Lesson.DAY_OF_WEEK_CHOICES}
        for lesson in lessons.order_by('start_time'):
            schedule[lesson.day_of_week].append(lesson)
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
