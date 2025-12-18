from django import forms
from .models import StudyMaterial

class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ["title", "description", "file", "batch", "subject"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control bg-light border-0"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control bg-light border-0",
                "rows": 3
            }),
            "file": forms.ClearableFileInput(attrs={
                "class": "form-control bg-light border-0",
                "accept": ".pdf,.doc,.docx,.ppt,.pptx,.jpg,.jpeg,.png"
            }),
            "batch": forms.Select(attrs={
                "class": "form-control bg-light border-0"
            }),
            "subject": forms.Select(attrs={
                "class": "form-control bg-light border-0"
            }),
        }
