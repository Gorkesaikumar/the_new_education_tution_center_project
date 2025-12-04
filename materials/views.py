from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import StudyMaterial
from .forms import StudyMaterialForm

def is_teacher(user):
    return user.is_authenticated and user.is_teacher

@login_required
@user_passes_test(is_teacher)
def material_list(request):
    materials = StudyMaterial.objects.all().order_by('-uploaded_at')
    return render(request, 'materials/material_list.html', {'materials': materials})

@login_required
@user_passes_test(is_teacher)
def material_upload(request):
    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            material.save()
            messages.success(request, 'Material uploaded successfully.')
            return redirect('material_list')
    else:
        form = StudyMaterialForm()
    return render(request, 'materials/material_form.html', {'form': form})

@login_required
@user_passes_test(is_teacher)
def material_delete(request, pk):
    material = get_object_or_404(StudyMaterial, pk=pk)
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Material deleted successfully.')
        return redirect('material_list')
    return render(request, 'materials/material_confirm_delete.html', {'material': material})

@login_required
def student_materials(request):
    if not request.user.is_student:
        return redirect('dashboard')
    
    # Filter materials for the student's batch
    student_batch = request.user.student_profile.batch
    materials = StudyMaterial.objects.filter(batch=student_batch).order_by('-uploaded_at')
    
    return render(request, 'materials/student_materials.html', {'materials': materials})
