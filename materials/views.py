import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist

from .models import StudyMaterial
from .forms import StudyMaterialForm
from students.models import StudentProfile

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Role checks (Django-native, production-safe)
# --------------------------------------------------

def is_teacher(user):
    return user.is_authenticated and user.groups.filter(name="Teacher").exists()


def is_student(user):
    return user.is_authenticated and user.groups.filter(name="Student").exists()


# --------------------------------------------------
# Teacher Views
# --------------------------------------------------

@login_required
@user_passes_test(is_teacher, login_url="dashboard")
def material_list(request):
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
    if request.method == "POST":
        form = StudyMaterialForm(request.POST, request.FILES)

        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            material.save()

            messages.success(request, "Study material uploaded successfully.")
            return redirect("material_list")
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
    material = get_object_or_404(StudyMaterial, pk=pk)

    if request.method == "POST":
        title = material.title

        # Delete file from storage first
        if material.file:
            try:
                material.file.delete(save=False)
            except Exception:
                logger.exception("Failed to delete GCS file for material %s", pk)

        material.delete()
        messages.success(request, f'Study material "{title}" deleted successfully.')
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
    if not is_student(request.user):
        return redirect("dashboard")

    materials = StudyMaterial.objects.none()

    try:
        student_profile = StudentProfile.objects.get(user=request.user)

        if not student_profile.batch:
            messages.info(request, "You are not assigned to any batch yet.")
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
        messages.error(
            request,
            "Student profile not found. Please contact administration."
        )

    return render(
        request,
        "materials/student_materials.html",
        {"materials": materials}
    )
