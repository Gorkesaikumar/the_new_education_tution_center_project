import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .models import StudyMaterial
from .forms import StudyMaterialForm
from students.models import StudentProfile

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Role checks (PRODUCTION SAFE)
# --------------------------------------------------

def is_teacher(user):
    """
    Teachers OR superusers can manage materials.
    """
    return (
        user.is_authenticated
        and (user.is_superuser or user.groups.filter(name="Teacher").exists())
    )


def is_student(user):
    """
    Students only (superusers are NOT students).
    """
    return (
        user.is_authenticated
        and user.groups.filter(name="Student").exists()
    )


# --------------------------------------------------
# Teacher Views
# --------------------------------------------------

@login_required
@user_passes_test(is_teacher, login_url="dashboard")
def material_list(request):
    """
    List all study materials for teachers/admins.
    """
    materials = (
        StudyMaterial.objects
        .select_related("batch", "subject", "uploaded_by")
        .order_by("-uploaded_at")
    )

    return render(
        request,
        "materials/material_list.html",
        {"materials": materials}
    )


@login_required
@user_passes_test(is_teacher, login_url="dashboard")
def material_upload(request):
    """
    Upload new study material.
    """
    if request.method == "POST":
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
                return redirect("material_list")

            except Exception:
                logger.exception("Failed to upload study material")
                messages.error(
                    request,
                    "Upload failed. Please try again."
                )
    else:
        form = StudyMaterialForm()

    return render(
        request,
        "materials/material_form.html",
        {"form": form}
    )


@login_required
@user_passes_test(is_teacher, login_url="dashboard")
def material_delete(request, pk):
    """
    Delete study material + file from GCS.
    """
    material = get_object_or_404(
        StudyMaterial.objects.select_related("batch", "subject"),
        pk=pk
    )

    if request.method == "POST":
        title = material.title

        if material.file:
            try:
                material.file.delete(save=False)
            except Exception:
                logger.exception(
                    "Failed to delete GCS file for material pk=%s",
                    material.pk
                )

        material.delete()

        messages.success(
            request,
            f'Study material "{title}" deleted successfully.'
        )
        return redirect("material_list")

    return render(
        request,
        "materials/material_confirm_delete.html",
        {"material": material}
    )


# --------------------------------------------------
# Student Views
# --------------------------------------------------

@login_required
def student_materials(request):
    """
    List materials for the student's batch.
    """
    if not is_student(request.user):
        return redirect("dashboard")

    materials = StudyMaterial.objects.none()

    try:
        student_profile = StudentProfile.objects.select_related(
            "batch"
        ).get(user=request.user)

        if not student_profile.batch:
            messages.info(
                request,
                "You are not assigned to any batch yet."
            )
            return render(
                request,
                "materials/student_materials.html",
                {"materials": materials}
            )

        materials = (
            StudyMaterial.objects
            .filter(batch=student_profile.batch)
            .select_related("batch", "subject", "uploaded_by")
            .order_by("-uploaded_at")
        )

    except StudentProfile.DoesNotExist:
        logger.warning(
            "StudentProfile missing for user pk=%s",
            request.user.pk
        )
        messages.error(
            request,
            "Student profile not found. Please contact administration."
        )

    return render(
        request,
        "materials/student_materials.html",
        {"materials": materials}
    )
