from django import forms
from .models import Exam, Mark

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'batch', 'subject', 'date', 'total_marks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
