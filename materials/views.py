import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .models import StudyMaterial
from .forms import StudyMaterialForm

logger = logging.getLogger(__name__)


# ---------------------------
# Access Control Helpers
# ---------------------------

def is_teacher(user):
    return user.is_authenticated and getattr(user, 'is_teacher', False)


# ---------------------------
# Teacher Views
# ---------------------------

@login_required
@user_passes_test(is_teacher, login_url='dashboard')
def material_list(request):
    """
    List all study materials for teachers.
    Safe against DB failures and missing relations.
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
        messages.error(
            request,
            "Unable to load study materials right now. Please try again later."
        )

    return render(
        request,
        'materials/material_list.html',
        {'materials': materials}
    )


@login_required
@user_passes_test(is_teacher, login_url='dashboard')
def material_upload(request):
    """
    Upload study material.
    Handles file upload to GCS safely.
    """
    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                material = form.save(commit=False)
                material.uploaded_by = request.user
                material.save()

                messages.success(
                    request,
                    "Study material uploaded successfully."
                )
                return redirect('material_list')

            except Exception:
                logger.exception("Failed to save study material")
                messages.error(
                    request,
                    "Upload failed due to a server error. Please try again."
                )
    else:
        form = StudyMaterialForm()

    return render(
        request,
        'materials/material_form.html',
        {'form': form}
    )


@login_required
@user_passes_test(is_teacher, login_url='dashboard')
def material_delete(request, pk):
    """
    Delete study material.
    Deletes file from GCS first, then DB record.
    """
    material = get_object_or_404(
        StudyMaterial.objects.select_related('batch', 'subject', 'uploaded_by'),
        pk=pk
    )

    if request.method == 'POST':
        material_title = material.title

        # Delete file from storage if it exists
        if material.file and material.file.name:
            try:
                material.file.delete(save=False)
            except Exception:
                logger.exception(
                    "Failed to delete file from storage for material pk=%s",
                    material.pk
                )

        try:
            material.delete()
            messages.success(
                request,
                f'Study material "{material_title}" deleted successfully.'
            )
        except Exception:
            logger.exception(
                "Failed to delete study material from DB pk=%s",
                material.pk
            )
            messages.error(
                request,
                "Failed to delete material. Please try again."
            )
            return redirect('material_list')

        return redirect('material_list')

    return render(
        request,
        'materials/material_confirm_delete.html',
        {'material': material}
    )


# ---------------------------
# Student Views
# ---------------------------

@login_required
def student_materials(request):
    """
    List study materials for the logged-in student.
    Fully defensive against missing profile or batch.
    """
    if not getattr(request.user, 'is_student', False):
        return redirect('dashboard')

    materials = StudyMaterial.objects.none()

    try:
        student_profile = getattr(request.user, 'student_profile', None)

        if student_profile is None:
            logger.warning(
                "Student user %s has no student_profile",
                request.user.pk
            )
            messages.warning(
                request,
                "Your student profile is not set up. Please contact administration."
            )
            return render(
                request,
                'materials/student_materials.html',
                {'materials': materials}
            )

        student_batch = getattr(student_profile, 'batch', None)

        if student_batch is None:
            logger.warning(
                "Student %s has no batch assigned",
                request.user.pk
            )
            messages.info(
                request,
                "You are not assigned to any batch yet."
            )
            return render(
                request,
                'materials/student_materials.html',
                {'materials': materials}
            )

        materials = (
            StudyMaterial.objects
            .filter(batch=student_batch)
            .select_related('batch', 'subject', 'uploaded_by')
            .order_by('-uploaded_at')
        )

    except Exception:
        logger.exception(
            "Failed to fetch student materials for user pk=%s",
            request.user.pk
        )
        messages.error(
            request,
            "Unable to load study materials right now."
        )

    return render(
        request,
        'materials/student_materials.html',
        {'materials': materials}
    )
