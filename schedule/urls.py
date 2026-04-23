from django.urls import path
from .views import GroupListView, GroupScheduleView, FilteredScheduleView, teacher_autocomplete, TeacherSearchView, ClassroomSearchView, classroom_autocomplete

app_name = 'schedule'

urlpatterns = [
    path('', GroupListView.as_view(), name='group_list'),
    path('group/<int:pk>/', GroupScheduleView.as_view(), name='group_schedule'),
    
    path('api/teacher-autocomplete/', teacher_autocomplete, name='teacher_autocomplete'),
    path('api/classroom-autocomplete/', classroom_autocomplete, name='classroom_autocomplete'),
    
    path('teacher/search/', TeacherSearchView.as_view(), name='teacher_search'),
    path('classroom/search/', ClassroomSearchView.as_view(), name='classroom_search'),
    
    path('teacher/<slug:teacher_slug>/', TeacherSearchView.as_view(), name='teacher_by_slug'),
    path('classroom/<slug:classroom_slug>/', ClassroomSearchView.as_view(), name='classroom_by_slug'),
    
    path('teacher/<int:teacher_pk>/', FilteredScheduleView.as_view(), name='teacher_schedule'),
    path('classroom/<int:classroom_pk>/', FilteredScheduleView.as_view(), name='classroom_schedule'),
    path('subject/<int:subject_pk>/', FilteredScheduleView.as_view(), name='subject_schedule'),
]
