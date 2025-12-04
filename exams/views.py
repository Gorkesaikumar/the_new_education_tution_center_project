from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Exam, Mark
from .forms import ExamForm
from students.models import StudentProfile

def is_teacher(user):
    return user.is_authenticated and user.is_teacher

@login_required
@user_passes_test(is_teacher)
def exam_list(request):
    exams = Exam.objects.all().order_by('-date')
    return render(request, 'exams/exam_list.html', {'exams': exams})

@login_required
@user_passes_test(is_teacher)
def exam_create(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam created successfully.')
            return redirect('exam_list')
    else:
        form = ExamForm()
    return render(request, 'exams/exam_form.html', {'form': form})

@login_required
@user_passes_test(is_teacher)
def exam_marks(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    students = exam.batch.students.all()
    
    if request.method == 'POST':
        for student in students:
            marks_obtained = request.POST.get(f'marks_{student.user.id}')
            if marks_obtained:
                Mark.objects.update_or_create(
                    exam=exam,
                    student=student.user,
                    defaults={'marks_obtained': marks_obtained}
                )
        messages.success(request, 'Marks updated successfully.')
        return redirect('exam_list')

    # Fetch existing marks
    existing_marks = Mark.objects.filter(exam=exam)
    marks_map = {mark.student.id: mark.marks_obtained for mark in existing_marks}

    return render(request, 'exams/exam_marks.html', {
        'exam': exam,
        'students': students,
        'marks_map': marks_map
    })

@login_required
def student_marks(request):
    if not request.user.is_student:
        return redirect('dashboard')
    
    marks = Mark.objects.filter(student=request.user).order_by('-exam__date')
    return render(request, 'exams/student_marks.html', {'marks': marks})
