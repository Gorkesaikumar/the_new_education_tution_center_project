from django import forms
from .models import Announcement

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'target_type', 'target_batches']
        widgets = {
            'target_batches': forms.CheckboxSelectMultiple(),
        }
