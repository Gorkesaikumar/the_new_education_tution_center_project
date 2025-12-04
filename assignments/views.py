from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm
from django.utils import timezone

def is_teacher(user):
    return user.is_authenticated and user.is_teacher

@login_required
def assignment_list(request):
    if request.user.is_teacher:
        assignments = Assignment.objects.all().order_by('-created_at')
    else:
        # Student sees assignments for their batch
        student_batch = request.user.student_profile.batch
        assignments = Assignment.objects.filter(batch=student_batch).order_by('-due_date')
    
    return render(request, 'assignments/assignment_list.html', {'assignments': assignments})

@login_required
@user_passes_test(is_teacher)
def assignment_create(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, 'Assignment created successfully.')
            return redirect('assignment_list')
    else:
        form = AssignmentForm()
    return render(request, 'assignments/assignment_form.html', {'form': form})

@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    submission = None
    if request.user.is_student:
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
    
    if request.method == 'POST' and request.user.is_student:
        if submission:
            messages.warning(request, 'You have already submitted this assignment.')
        else:
            form = SubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                sub = form.save(commit=False)
                sub.assignment = assignment
                sub.student = request.user
                sub.save()
                messages.success(request, 'Assignment submitted successfully.')
                return redirect('assignment_detail', pk=pk)
    else:
        form = SubmissionForm()

    return render(request, 'assignments/assignment_detail.html', {
        'assignment': assignment,
        'submission': submission,
        'form': form
    })

@login_required
@user_passes_test(is_teacher)
def view_submissions(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    submissions = assignment.submissions.all()
    return render(request, 'assignments/view_submissions.html', {'assignment': assignment, 'submissions': submissions})
