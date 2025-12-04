from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import StudentProfile
from .forms import StudentUserForm, StudentProfileForm
from django.contrib.auth import get_user_model

User = get_user_model()

def is_teacher(user):
    return user.is_authenticated and user.is_teacher

@login_required
@user_passes_test(is_teacher)
def student_list(request):
    students = StudentProfile.objects.all()
    return render(request, 'students/student_list.html', {'students': students})

@login_required
@user_passes_test(is_teacher)
def student_create(request):
    if request.method == 'POST':
        user_form = StudentUserForm(request.POST)
        profile_form = StudentProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Student created successfully.')
            return redirect('student_list')
    else:
        user_form = StudentUserForm()
        profile_form = StudentProfileForm()
    return render(request, 'students/student_form.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
@user_passes_test(is_teacher)
def student_update(request, pk):
    profile = get_object_or_404(StudentProfile, pk=pk)
    user = profile.user
    if request.method == 'POST':
        user_form = StudentUserForm(request.POST, instance=user)
        # We don't want to require password on update usually, but for simplicity let's keep it or handle it.
        # If we want to allow updating without password, we need a different form or logic.
        # Let's assume for now admin resets password or we make it optional.
        # For simplicity, let's use a different form for update that excludes password or makes it optional.
        # But to stick to the requested "working code", I'll just use the same form but handle password carefully.
        # Actually, let's just exclude password from update for now to avoid complexity, or allow admin to set it.
        # I'll create a StudentUserUpdateForm inline or just use the same one but make password optional.
        # Let's just use the same form but ignore password if empty.
        
        # Re-initializing form with instance
        user_form = StudentUserForm(request.POST, instance=user)
        user_form.fields['password'].required = False
        
        profile_form = StudentProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            if user_form.cleaned_data['password']:
                user.set_password(user_form.cleaned_data['password'])
            user.save()
            profile_form.save()
            messages.success(request, 'Student updated successfully.')
            return redirect('student_list')
    else:
        user_form = StudentUserForm(instance=user)
        user_form.fields['password'].required = False
        profile_form = StudentProfileForm(instance=profile)
    return render(request, 'students/student_form.html', {'user_form': user_form, 'profile_form': profile_form, 'is_update': True})

@login_required
@user_passes_test(is_teacher)
def student_delete(request, pk):
    profile = get_object_or_404(StudentProfile, pk=pk)
    if request.method == 'POST':
        profile.user.delete() # This cascades to profile
        messages.success(request, 'Student deleted successfully.')
        return redirect('student_list')
    return render(request, 'students/student_confirm_delete.html', {'student': profile})
