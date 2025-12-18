from django import forms
from .models import StudyMaterial
from batches.models import Batch, Subject


class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ['title', 'description', 'file', 'batch', 'subject']
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter material title"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Optional description"
            }),
            "file": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": ".pdf,.doc,.docx,.ppt,.pptx,.jpg,.jpeg,.png"
            }),
            "batch": forms.Select(attrs={
                "class": "form-select"
            }),
            "subject": forms.Select(attrs={
                "class": "form-select"
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Always restrict subjects until batch is selected
        self.fields["subject"].queryset = Subject.objects.none()

        if self.instance.pk and self.instance.batch:
            self.fields["subject"].queryset = Subject.objects.filter(
                batch=self.instance.batch
            )

        if "batch" in self.data:
            try:
                batch_id = int(self.data.get("batch"))
                self.fields["subject"].queryset = Subject.objects.filter(
                    batch_id=batch_id
                )
            except (ValueError, TypeError):
                pass
