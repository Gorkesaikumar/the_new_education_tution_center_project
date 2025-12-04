from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import EnquiryForm
from .models import Enquiry

def submit_enquiry(request):
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your enquiry has been submitted successfully! We will contact you soon.')
            return redirect('home')
        else:
            messages.error(request, 'There was an error submitting your enquiry. Please check the form and try again.')
            # In a real scenario, we might want to render the home page with errors, 
            # but for now, redirecting back to home is simplest for a landing page form.
            return redirect('home')
    return redirect('home')

def is_teacher_or_admin(user):
    return user.is_authenticated and (user.is_teacher or user.is_staff or user.is_superuser)

from django.http import JsonResponse

@login_required
@user_passes_test(is_teacher_or_admin)
def enquiry_list(request):
    # Mark all unread enquiries as read when the list is viewed
    Enquiry.objects.filter(is_read=False).update(is_read=True)
    enquiries = Enquiry.objects.all()
    return render(request, 'enquiries/enquiry_list.html', {'enquiries': enquiries})

@login_required
@user_passes_test(is_teacher_or_admin)
def get_unread_count(request):
    count = Enquiry.objects.filter(is_read=False).count()
    return JsonResponse({'count': count})
