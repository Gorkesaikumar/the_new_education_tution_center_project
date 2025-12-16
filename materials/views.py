import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.files.storage import default_storage

from .models import StudyMaterial
from .forms import StudyMaterialForm

logger = logging.getLogger(__name__)


def is_teacher(user):
    return user.is_authenticated and getattr(user, 'is_teacher', False)


@login_required
@user_passes_test(is_teacher)
def material_list(request):
    """
    List all study materials for teachers.
    Production-safe: handles database errors gracefully.
    """
    materials = StudyMaterial.objects.none()
    try:
        materials = (
            StudyMaterial.objects
            .select_related('batch', 'subject', 'uploaded_by')
            .order_by('-uploaded_at')
        )
    except Exception:
        logger.exception("Failed to fetch materials in material_list view")
        messages.error(request, "Unable to load materials. Please try again later.")
    
    return render(request, 'materials/material_list.html', {'materials': materials})


@login_required
@user_passes_test(is_teacher)
def material_upload(request):
    """
    Handle material upload for teachers.
    Production-safe: logs upload failures.
    """
    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                material = form.save(commit=False)
                material.uploaded_by = request.user
                material.save()
                messages.success(request, 'Material uploaded successfully.')
                return redirect('material_list')
            except Exception:
                logger.exception("Failed to save material during upload")
                messages.error(request, "Failed to upload material. Please try again.")
    else:
        form = StudyMaterialForm()
    
    return render(request, 'materials/material_form.html', {'form': form})


@login_required
@user_passes_test(is_teacher)
def material_delete(request, pk):
    """
    Handle material deletion for teachers.
    Production-safe: explicitly deletes file from storage before model deletion.
    Gracefully handles missing GCS objects.
    """
    material = get_object_or_404(
        StudyMaterial.objects.select_related('batch', 'subject', 'uploaded_by'),
        pk=pk
    )
    
    if request.method == 'POST':
        material_title = material.title
        
        # Explicitly delete the file from storage before deleting the model
        if material.file:
            try:
                file_name = material.file.name
                material.file.delete(save=False)
                logger.info("Deleted file from storage: %s", file_name)
            except Exception:
                # Log but don't crash - file might already be missing from GCS
                logger.exception("Failed to delete file from storage for material pk=%s", pk)
        
        try:
            material.delete()
            messages.success(request, f'Material "{material_title}" deleted successfully.')
        except Exception:
            logger.exception("Failed to delete material pk=%s from database", pk)
            messages.error(request, "Failed to delete material. Please try again.")
            return redirect('material_list')
        
        return redirect('material_list')
    
    return render(request, 'materials/material_confirm_delete.html', {'material': material})


@login_required
def student_materials(request):
    """
    List study materials for the student's batch.
    Production-safe: handles missing student_profile and batch gracefully.
    """
    # Check if user is a student
    if not getattr(request.user, 'is_student', False):
        return redirect('dashboard')
    
    materials = StudyMaterial.objects.none()
    
    try:
        # Safely get student_profile - might not exist
        student_profile = getattr(request.user, 'student_profile', None)
        
        if student_profile is None:
            logger.warning(
                "User %s (pk=%s) is_student=True but has no student_profile",
                request.user.username,
                request.user.pk
            )
            messages.warning(request, "Your student profile is not set up. Please contact administration.")
            return render(request, 'materials/student_materials.html', {'materials': materials})
        
        # Safely get batch - might be None
        student_batch = getattr(student_profile, 'batch', None)
        
        if student_batch is None:
            logger.warning(
                "Student %s (pk=%s) has no batch assigned",
                request.user.username,
                request.user.pk
            )
            messages.info(request, "You are not assigned to any batch yet.")
            return render(request, 'materials/student_materials.html', {'materials': materials})
        
        materials = (
            StudyMaterial.objects
            .filter(batch=student_batch)
            .select_related('batch', 'subject', 'uploaded_by')
            .order_by('-uploaded_at')
        )
        
    except Exception:
        logger.exception("Failed to fetch materials in student_materials view for user pk=%s", request.user.pk)
        messages.error(request, "Unable to load materials. Please try again later.")
    
    return render(request, 'materials/student_materials.html', {'materials': materials})
