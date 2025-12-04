from django import forms
from django.contrib.auth import get_user_model
from .models import StudentProfile

User = get_user_model()

class StudentUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        user.is_student = True
        if commit:
            user.save()
        return user

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['batch', 'phone_number', 'address', 'date_of_birth', 'date_of_join']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_of_join': forms.DateInput(attrs={'type': 'date'}),
        }

class PublicRegistrationForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, initial='student')
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        role = cleaned_data.get("role")
        phone_number = cleaned_data.get("phone_number")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        if role == 'student' and not phone_number:
             self.add_error('phone_number', 'Phone number is required for students.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        role = self.cleaned_data.get('role')
        if role == 'student':
            user.is_student = True
        elif role == 'teacher':
            user.is_teacher = True
            
        if commit:
            user.save()
            if role == 'student':
                StudentProfile.objects.create(
                    user=user,
                    phone_number=self.cleaned_data.get('phone_number'),
                    address=self.cleaned_data.get('address')
                )
        return user
