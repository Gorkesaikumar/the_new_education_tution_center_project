from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import AttendanceRecord
from batches.models import Batch
from students.models import StudentProfile
from django.utils import timezone
from datetime import datetime

def is_teacher(user):
    return user.is_authenticated and user.is_teacher

@login_required
@user_passes_test(is_teacher)
def attendance_dashboard(request):
    batches = Batch.objects.all()
    return render(request, 'attendance/attendance_dashboard.html', {'batches': batches})

@login_required
@user_passes_test(is_teacher)
def mark_attendance(request, batch_id):
    batch = get_object_or_404(Batch, pk=batch_id)
    students = batch.students.all()
    date = request.GET.get('date', timezone.now().date().isoformat())
    
    if request.method == 'POST':
        date = request.POST.get('date')
        for student in students:
            status = request.POST.get(f'status_{student.user.id}')
            AttendanceRecord.objects.update_or_create(
                batch=batch,
                student=student.user,
                date=date,
                defaults={'status': status}
            )
        messages.success(request, 'Attendance marked successfully.')
        return redirect('attendance_dashboard')

    # Fetch existing attendance for this date
    existing_records = AttendanceRecord.objects.filter(batch=batch, date=date)
    attendance_map = {record.student.id: record.status for record in existing_records}

    return render(request, 'attendance/mark_attendance.html', {
        'batch': batch,
        'students': students,
        'date': date,
        'attendance_map': attendance_map
    })

@login_required
@user_passes_test(is_teacher)
def view_attendance(request, batch_id):
    batch = get_object_or_404(Batch, pk=batch_id)
    records = AttendanceRecord.objects.filter(batch=batch).order_by('-date')
    return render(request, 'attendance/view_attendance.html', {'batch': batch, 'records': records})

@login_required
def student_attendance(request):
    if not request.user.is_student:
        return redirect('dashboard')
    
    records = AttendanceRecord.objects.filter(student=request.user).order_by('-date')
    total_present = records.filter(status='PRESENT').count()
    total_absent = records.filter(status='ABSENT').count()
    
    return render(request, 'attendance/student_attendance.html', {
        'records': records,
        'total_present': total_present,
        'total_absent': total_absent
    })
