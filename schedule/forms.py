from django import forms

class ImportForm(forms.Form):
    file = forms.FileField(label='Файл docx', widget=forms.ClearableFileInput(attrs={'accept': '.docx'}))
    clear = forms.BooleanField(label='Очистить расписание перед импортом', required=False)