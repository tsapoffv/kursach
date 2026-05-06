import os
import re
from docx import Document
from datetime import time
from slugify import slugify
from schedule.models import Group, Teacher, Classroom, Subject, Lesson, TimeSlot


DAYS_ORDER = ['ПОНЕДЕЛЬНИК', 'ВТОРНИК', 'СРЕДА', 'ЧЕТВЕРГ', 'ПЯТНИЦА', 'СУББОТА']
DAYS_MAP = {'понедельник': 1, 'вторник': 2, 'среда': 3, 'четверг': 4, 'пятница': 5, 'суббота': 6}


def extract_course_from_doc(doc: Document) -> int:
    """Извлекает курс из документа"""
    for para in doc.paragraphs:
        text = para.text.strip().lower()
        match = re.search(r'(\d+)\s*курс', text)
        if match:
            return int(match.group(1))
    return 1


def find_schedule_table(doc: Document):
    """Находит таблицу с расписанием по характерным признакам"""
    for table in doc.tables:
        if len(table.rows) < 3:
            continue
        first_row = [c.text.strip().lower() for c in table.rows[0].cells]
        if 'время' in first_row and 'дисциплины' in first_row:
            return table
    
    for table in doc.tables:
        for row in table.rows[:5]:
            row_text = ' '.join([cell.text for cell in row.cells]).lower()
            if 'понедельник' in row_text and 'вторник' in row_text:
                return table
    
    return doc.tables[0] if doc.tables else None


def parse_docx(file_path: str, clear: bool = False):
    """Импорт расписания из docx файла по указанному пути"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'Файл не найден: {file_path}')

    if clear:
        _clear_db()

    doc = Document(file_path)
    return _parse_doc(doc)


def parse_docx_file(file_obj, clear: bool = False):
    """Импорт расписания из файлового объекта (для загрузки через веб)"""
    if clear:
        _clear_db()

    doc = Document(file_obj)
    return _parse_doc(doc)


def _clear_db():
    """Очистка базы данных"""
    Lesson.objects.all().delete()
    Group.objects.all().delete()
    Teacher.objects.all().delete()
    Classroom.objects.all().delete()
    Subject.objects.all().delete()


def _parse_doc(doc: Document) -> dict:
    """Парсит документ docx"""
    schedule_table = find_schedule_table(doc)
    
    if not schedule_table:
        return {'lessons': 0, 'errors': ['Таблица с расписанием не найдена']}

    course = extract_course_from_doc(doc)
    
    lessons_created = 0
    errors = []
    current_day = None
    known_groups = []
    all_students_lessons = []

    for row in schedule_table.rows:
        cells = row.cells
        if not cells:
            continue

        all_cells_text = [c.text.strip() for c in cells]
        all_cells_lower = [t.lower() for t in all_cells_text]

        day_found = False
        for i, cell_text in enumerate(all_cells_lower):
            for day in DAYS_ORDER:
                if day in cell_text.upper() and len(cell_text) < 20:
                    current_day = DAYS_MAP[day.lower()]
                    day_found = True
                    break
            if day_found:
                break

        if day_found:
            continue

        first_cell = all_cells_text[0]
        time_pattern = r'\d{1,2}\.\d{2}-\d{1,2}\.\d{2}'
        time_match = re.search(time_pattern, first_cell)
        
        if not time_match:
            continue

        time_str = first_cell.strip()
        
        time_slot = _get_or_create_time_slot(time_str)
        
        discipline = all_cells_text[1] if len(cells) > 1 else ""
        group_info = all_cells_text[2] if len(cells) > 2 else ""
        lesson_type_str = all_cells_text[3] if len(cells) > 3 else ""
        teacher_name = all_cells_text[4] if len(cells) > 4 else ""
        room_name = all_cells_text[5] if len(cells) > 5 else ""

        if not current_day or not discipline:
            continue

        week_type = 'BOTH'
        
        group_name = _parse_group_name(group_info)
        if group_name is None:
            continue
        
        if group_name == 'ALL':
            all_students_lessons.append({
                'discipline': discipline,
                'time_slot': time_slot,
                'teacher_name': teacher_name,
                'room_name': room_name,
                'lesson_type_str': lesson_type_str,
                'current_day': current_day,
                'week_type': week_type
            })
            continue

        group = Group.objects.filter(name=group_name, course=course).first()
        if not group:
            group = Group.objects.create(name=group_name, course=course)
        known_groups.append(group)
        
        lesson_count = _create_lesson(
            group=group,
            discipline=discipline,
            time_slot=time_slot,
            teacher_name=teacher_name,
            room_name=room_name,
            lesson_type_str=lesson_type_str,
            day=current_day,
            week_type=week_type,
            errors=errors,
            time_str=time_str
        )
        lessons_created += lesson_count

    for all_lesson in all_students_lessons:
        for group in known_groups:
            if group.course != course:
                continue
            lesson_count = _create_lesson(
                group=group,
                discipline=all_lesson['discipline'],
                time_slot=all_lesson['time_slot'],
                teacher_name=all_lesson['teacher_name'],
                room_name=all_lesson['room_name'],
                lesson_type_str=all_lesson['lesson_type_str'],
                day=all_lesson['current_day'],
                week_type=all_lesson['week_type'],
                errors=errors,
                time_str=""
            )
            lessons_created += lesson_count

    return {'lessons': lessons_created, 'errors': errors}


def _create_lesson(group, discipline, time_slot, teacher_name, room_name, lesson_type_str, day, week_type, errors, time_str):
    """Создает занятие и возвращает количество созданных (0 или 1)"""
    subject, _ = Subject.objects.get_or_create(name=discipline)

    teacher = None
    if teacher_name:
        clean_teacher = _clean_teacher_name(teacher_name)
        if clean_teacher:
            slug = slugify(clean_teacher)
            defaults = {'slug': slug} if slug else {}
            teacher, created = Teacher.objects.get_or_create(
                name=clean_teacher,
                defaults=defaults
            )
            if not created and teacher.slug is None and slug:
                teacher.slug = slug
                teacher.save()

    classroom = None
    if room_name:
        slug = slugify(room_name)
        if slug:
            classroom, created = Classroom.objects.get_or_create(
                name=room_name,
                defaults={'slug': slug}
            )
            if not created and classroom.slug is None:
                classroom.slug = slug
                classroom.save()

    lesson_type = _parse_lesson_type(lesson_type_str)

    existing = Lesson.objects.filter(
        group=group,
        subject=subject,
        time_slot=time_slot,
        day_of_week=day,
        week_type=week_type
    ).first()

    if existing:
        return 0

    try:
        Lesson.objects.create(
            group=group,
            subject=subject,
            teacher=teacher,
            classroom=classroom,
            time_slot=time_slot,
            day_of_week=day,
            week_type=week_type,
            lesson_type=lesson_type
        )
        return 1
    except Exception as e:
        errors.append(f'{time_str} {discipline}: {str(e)}')
        return 0


def _parse_time(time_str: str):
    """Парсит время в формате XX.XX-XX.XX"""
    pattern = r'(\d{2})\.(\d{2})-'
    match = re.search(pattern, time_str)
    
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        return time(hour, minute)
    
    return time(9, 0)


def _get_or_create_time_slot(time_str: str):
    """Получает или создает TimeSlot на основе строки времени"""
    pattern = r'(\d{1,2})\.(\d{2})-(\d{1,2})\.(\d{2})'
    match = re.search(pattern, time_str)
    
    if match:
        start = time(int(match.group(1)), int(match.group(2)))
        end = time(int(match.group(3)), int(match.group(4)))
        
        ts = TimeSlot.objects.filter(start_time=start, end_time=end).first()
        if ts:
            return ts
        
        name = f"{int(match.group(1)):02d}.{match.group(2)}-{int(match.group(3)):02d}.{match.group(4)}"
        return TimeSlot.objects.create(name=name, start_time=start, end_time=end)
    
    return None


def _parse_group_name(group_info: str) -> str:
    """Парсит название группы из строки"""
    if not group_info:
        return None
    
    group_info = group_info.replace('\n', ' ').strip()
    
    if 'все студенты' in group_info.lower():
        return 'ALL'
    
    match = re.match(r'(\d+)\s*группа', group_info.lower())
    if match:
        return f"{match.group(1)} группа"
    
    match = re.match(r'(\d+)\s*подгруппа', group_info.lower())
    if match:
        return f"{match.group(1)} подгруппа"
    
    if group_info:
        return group_info.split()[0] if group_info.split() else None
    
    return None


def _clean_teacher_name(teacher_name: str) -> str:
    """Очищает ФИО преподавателя от служебных префиксов"""
    if not teacher_name:
        return None
    
    parts = teacher_name.split()
    if not parts:
        return None
    
    prefixes = ['преп.', 'ст.', 'доц.', 'проф.', 'асс.', ' зав.']
    cleaned_parts = [p for p in parts if p not in prefixes]
    
    return ' '.join(cleaned_parts) if cleaned_parts else None


def create_default_time_slots():
    """Создает типичные временные слоты"""
    default_slots = [
        ("1 пара", "09:00", "10:30"),
        ("2 пара", "10:40", "12:10"),
        ("3 пара", "12:20", "13:50"),
        ("4 пара", "14:00", "15:30"),
        ("5 пара", "15:40", "17:10"),
        ("6 пара", "17:20", "18:50"),
    ]
    
    for name, start, end in default_slots:
        from datetime import time
        s = time(*map(int, start.split(':')))
        e = time(*map(int, end.split(':')))
        TimeSlot.objects.get_or_create(
            name=name,
            defaults={'start_time': s, 'end_time': e}
        )


def _parse_lesson_type(text: str) -> str:
    """Определяет тип занятия"""
    if not text:
        return 'LEC'
    
    text_clean = re.sub(r'\s*\(.*?\)', '', text)
    text_lower = text_clean.lower()
    
    if 'прак' in text_lower or 'семинар' in text_lower:
        return 'PRA'
    if 'лаб' in text_lower:
        return 'LAB'
    return 'LEC'


def parse_all_tables_verbose(file_path: str):
    """Отладочная функция - показывает структуру всех таблиц"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'Файл не найден: {file_path}')
    
    doc = Document(file_path)
    result = {'tables': []}
    
    for table_idx, table in enumerate(doc.tables):
        table_info = {
            'idx': table_idx,
            'rows': len(table.rows),
            'cols': len(table.columns),
            'preview': []
        }
        
        for row_idx, row in enumerate(table.rows[:10]):
            cells_text = [cell.text.strip()[:50] for cell in row.cells]
            table_info['preview'].append(cells_text)
        
        result['tables'].append(table_info)
    
    return result