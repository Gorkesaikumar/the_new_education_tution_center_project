from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import login
from django.db import models
from django.db.models import Sum
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from .models import Announcement
from .forms import AnnouncementForm
from students.models import StudentProfile
from batches.models import Batch
from exams.models import Exam
from fees.models import FeePayment
from students.forms import PublicRegistrationForm

def is_teacher(user):
    return user.is_authenticated and user.is_teacher

@login_required
def dashboard(request):
    if request.user.is_teacher:
        total_students = StudentProfile.objects.count()
        active_batches = Batch.objects.count()
        upcoming_exams = Exam.objects.order_by('date')[:5]
        total_fees = FeePayment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        recent_announcements = Announcement.objects.order_by('-created_at')[:5]
        
        context = {
            'total_students': total_students,
            'active_batches': active_batches,
            'upcoming_exams': upcoming_exams,
            'total_fees': total_fees,
            'recent_announcements': recent_announcements,
        }
        return render(request, 'core/teacher_dashboard.html', context)
    elif request.user.is_student:
        # Check if student profile exists (it should, but safety first)
        if hasattr(request.user, 'student_profile'):
            student_profile = request.user.student_profile
            batch = student_profile.batch
            recent_announcements = Announcement.objects.filter(
                models.Q(target_type='ALL') | 
                models.Q(target_batches=batch)
            ).distinct().order_by('-created_at')[:5]
            
            # Fetch upcoming exams for the student's batch
            from django.utils import timezone
            upcoming_exams = Exam.objects.filter(
                batch=batch, 
                date__gte=timezone.now().date()
            ).order_by('date')[:1]
            next_exam = upcoming_exams.first() if upcoming_exams.exists() else None

            # Fee Reminder Logic
            from datetime import timedelta
            today = timezone.now().date()
            join_date = student_profile.date_of_join
            days_since_join = (today - join_date).days
            
            fee_due = False
            if days_since_join > 30:
                last_payment = FeePayment.objects.filter(student=request.user).order_by('-date').first()
                if not last_payment:
                    fee_due = True
                else:
                    days_since_payment = (today - last_payment.date).days
                    if days_since_payment > 30:
                        fee_due = True

            context = {
                'student': student_profile,
                'batch': batch,
                'recent_announcements': recent_announcements,
                'next_exam': next_exam,
                'fee_due': fee_due,
            }
            return render(request, 'core/student_dashboard.html', context)
        else:
             # Fallback if student profile missing (shouldn't happen with new reg flow)
             return render(request, 'core/dashboard.html')
    else:
        return render(request, 'core/dashboard.html') # Fallback or admin

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PublicRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('dashboard')
    else:
        form = PublicRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
@user_passes_test(is_teacher)
def announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            form.save_m2m()
            messages.success(request, 'Announcement posted successfully.')
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()
    return render(request, 'core/announcement_form.html', {'form': form})

@login_required
def announcement_list(request):
    if request.user.is_teacher:
        announcements = Announcement.objects.all().order_by('-created_at')
    elif request.user.is_student:
        # Show global announcements and announcements for student's batch
        try:
            student_profile = request.user.student_profile
            student_batch = student_profile.batch
            announcements = Announcement.objects.filter(
                models.Q(target_type='ALL') | 
                models.Q(target_batches=student_batch)
            ).distinct().order_by('-created_at')
        except StudentProfile.DoesNotExist:
             # Fallback if profile missing: show only ALL
             announcements = Announcement.objects.filter(target_type='ALL').order_by('-created_at')
    else:
        announcements = Announcement.objects.none()
    
    return render(request, 'core/announcement_list.html', {'announcements': announcements})

@login_required
@user_passes_test(is_teacher)
def announcement_edit(request, pk):
    """
    Allow teachers to edit announcements.
    """
    announcement = Announcement.objects.get(pk=pk)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated successfully.')
            return redirect('announcement_list')
    else:
        form = AnnouncementForm(instance=announcement)
    
    return render(request, 'core/announcement_form.html', {'form': form, 'editing': True})

@login_required
@user_passes_test(is_teacher)
def announcement_delete(request, pk):
    """
    Allow teachers to delete announcements.
    """
    announcement = Announcement.objects.get(pk=pk)
    
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'Announcement deleted successfully.')
        return redirect('announcement_list')
    
    return render(request, 'core/announcement_confirm_delete.html', {'announcement': announcement})

@never_cache
def service_worker(request):
    """
    Serve the unified service worker (caching + FCM) from a template.
    This prevents clashes between two different SW registrations.
    """
    context = {
        'FIREBASE_API_KEY': settings.FIREBASE_API_KEY,
        'FIREBASE_AUTH_DOMAIN': settings.FIREBASE_AUTH_DOMAIN,
        'FIREBASE_PROJECT_ID': settings.FIREBASE_PROJECT_ID,
        'FIREBASE_STORAGE_BUCKET': settings.FIREBASE_STORAGE_BUCKET,
        'FIREBASE_MESSAGING_SENDER_ID': settings.FIREBASE_MESSAGING_SENDER_ID,
        'FIREBASE_APP_ID': settings.FIREBASE_APP_ID,
        'FIREBASE_MEASUREMENT_ID': settings.FIREBASE_MEASUREMENT_ID,
    }
    return render(request, 'sw.js', context, content_type='application/javascript')

@never_cache
def fcm_service_worker(request):
    """
    Also serve the same content at the default Firebase location as a fallback.
    """
    return service_worker(request)
