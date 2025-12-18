import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .models import StudyMaterial
from .forms import StudyMaterialForm

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Role checks (PRODUCTION SAFE)
# --------------------------------------------------

def is_teacher(user):
    """
    Check if user is a teacher.
    Uses the is_teacher boolean field on the User model, matching all other views.
    """
    return user.is_authenticated and getattr(user, 'is_teacher', False)


def is_student(user):
    """
    Check if user is a student.
    Uses the is_student boolean field on the User model.
    """
    return user.is_authenticated and getattr(user, 'is_student', False)


# --------------------------------------------------
# Teacher Views
# --------------------------------------------------

@login_required
@user_passes_test(is_teacher, login_url='/accounts/login/')
def material_list(request):
    """
    List all study materials for teachers/admins.
    Production-safe with try/except wrapper.
    """
    try:
        materials = (
            StudyMaterial.objects
            .select_related("batch", "subject", "uploaded_by")
            .order_by("-uploaded_at")
        )
    except Exception:
        logger.exception("Failed to fetch materials in material_list view")
        materials = StudyMaterial.objects.none()
        messages.error(request, "Unable to load materials. Please try again.")

    return render(
        request,
        "materials/material_list.html",
        {"materials": materials}
    )


@login_required
@user_passes_test(is_teacher, login_url='/accounts/login/')
def material_upload(request):
    """
    Handle material upload for teachers.
    """
    if request.method == "POST":
        form = StudyMaterialForm(
            request.POST,
            request.FILES,
            user=request.user
        )

        if form.is_valid():
            try:
                material = form.save(commit=False)
                material.uploaded_by = request.user
                material.save()
                messages.success(request, "Study material uploaded successfully.")
                return redirect("material_list")
            except Exception:
                logger.exception("Failed to save material during upload")
                messages.error(request, "Failed to upload material. Please try again.")
        else:
            logger.error("Material upload form errors: %s", form.errors)

    else:
        form = StudyMaterialForm(user=request.user)

    return render(
        request,
        "materials/material_form.html",
        {"form": form}
    )


@login_required
@user_passes_test(is_teacher, login_url='/accounts/login/')
def material_delete(request, pk):
    """
    Delete study material + file from storage.
    Production-safe with explicit file deletion.
    """
    material = get_object_or_404(
        StudyMaterial.objects.select_related("batch", "subject"),
        pk=pk
    )

    if request.method == "POST":
        title = material.title

        # Explicitly delete file from storage first
        if material.file:
            try:
                material.file.delete(save=False)
                logger.info("Deleted file from storage for material pk=%s", pk)
            except Exception:
                logger.exception(
                    "Failed to delete file for material pk=%s",
                    material.pk
                )

        try:
            material.delete()
            messages.success(
                request,
                f'Study material "{title}" deleted successfully.'
            )
        except Exception:
            logger.exception("Failed to delete material pk=%s from database", pk)
            messages.error(request, "Failed to delete material. Please try again.")

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
    Production-safe: handles missing student_profile gracefully.
    """
    if not is_student(request.user):
        return redirect("dashboard")

    materials = StudyMaterial.objects.none()

    try:
        # Safely get student_profile via related name
        student_profile = getattr(request.user, 'student_profile', None)

        if student_profile is None:
            logger.warning(
                "User %s (pk=%s) is_student=True but has no student_profile",
                request.user.username,
                request.user.pk
            )
            messages.warning(
                request,
                "Your student profile is not set up. Please contact administration."
            )
            return render(
                request,
                "materials/student_materials.html",
                {"materials": materials}
            )

        # Safely get batch - might be None
        student_batch = getattr(student_profile, 'batch', None)

        if student_batch is None:
            logger.info("Student %s has no batch assigned", request.user.username)
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
            .filter(batch=student_batch)
            .select_related("batch", "subject", "uploaded_by")
            .order_by("-uploaded_at")
        )

    except Exception:
        logger.exception(
            "Failed to fetch materials in student_materials view for user pk=%s",
            request.user.pk
        )
        messages.error(request, "Unable to load materials. Please try again.")

    return render(
        request,
        "materials/student_materials.html",
        {"materials": materials}
    )
