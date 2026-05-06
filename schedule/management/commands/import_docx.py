import os
from django.core.management.base import BaseCommand
from schedule.parser import parse_docx


class Command(BaseCommand):
    help = 'Импорт расписания из docx файла'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к docx файлу')
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить базу данных перед импортом',
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        clear = options.get('clear', False)
        
        try:
            result = parse_docx(file_path, clear=clear)
            
            if result['errors']:
                self.stdout.write(self.style.WARNING(f'Возникло {len(result["errors"])} ошибок:'))
                for error in result['errors'][:10]:
                    self.stdout.write(f'  - {error}')
                if len(result['errors']) > 10:
                    self.stdout.write(f'  ... и еще {len(result["errors"]) - 10} ошибок')

            self.stdout.write(self.style.SUCCESS(f'Успешно импортировано {result["lessons"]} занятий!'))
            
        except FileNotFoundError as e:
            self.stderr.write(self.style.ERROR(str(e)))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка при импорте: {e}'))