from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import FeePayment
from .forms import FeePaymentForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from students.models import StudentProfile
from django.utils import timezone

# import weasyprint # Optional for PDF, but user asked for simple implementation. 
# We will simulate PDF generation or use a simple HTML print view.

def is_teacher(user):
    return user.is_authenticated and user.is_teacher

@login_required
@user_passes_test(is_teacher)
def fee_list(request):
    payments = FeePayment.objects.all().order_by('-date')
    
    # Calculate fee status for all students
    # Calculate fee status for all students
    student_fee_status = []
    
    from django.db.models import OuterRef, Subquery, Max
    
    # Optimize: Fetch latest payment date for each student in one go
    latest_payments = FeePayment.objects.filter(
        student=OuterRef('user')
    ).order_by('-date').values('date')[:1]
    
    all_students = StudentProfile.objects.all().select_related('user', 'batch').annotate(
        last_payment_date=Subquery(latest_payments)
    )
    
    today = timezone.now().date()
    
    for student in all_students:
        join_date = student.date_of_join
        days_since_join = (today - join_date).days
        last_payment_date = student.last_payment_date
        
        is_due = False
        status = "Paid"
        due_date = None
        
        if days_since_join > 30:
            if not last_payment_date:
                is_due = True
                status = "Overdue (Never Paid)"
                due_date = join_date + timezone.timedelta(days=30)
            else:
                days_since_payment = (today - last_payment_date).days
                if days_since_payment > 30:
                    is_due = True
                    status = f"Overdue ({days_since_payment} days)"
                    due_date = last_payment_date + timezone.timedelta(days=30)
                else:
                    due_date = last_payment_date + timezone.timedelta(days=30)
        else:
            status = "New Student"
            due_date = join_date + timezone.timedelta(days=30)

        # Create a dummy object for last_payment to keep template compatible if needed, 
        # or just pass the date. The template uses {{ item.last_payment.date }}.
        # Let's pass a simple dict or object if needed, but since we only need date in template:
        last_payment_obj = {'date': last_payment_date} if last_payment_date else None

        student_fee_status.append({
            'student': student,
            'last_payment': last_payment_obj, 
            'is_due': is_due,
            'status': status,
            'due_date': due_date
        })

    return render(request, 'fees/fee_list.html', {
        'payments': payments,
        'student_fee_status': student_fee_status
    })

@login_required
@user_passes_test(is_teacher)
def record_payment(request):
    if request.method == 'POST':
        form = FeePaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment recorded successfully.')
            return redirect('fee_list')
    else:
        form = FeePaymentForm()
    return render(request, 'fees/fee_form.html', {'form': form})

@login_required
def fee_receipt(request, pk):
    payment = get_object_or_404(FeePayment, pk=pk)
    # Check permissions
    if not request.user.is_teacher and payment.student != request.user:
        return redirect('dashboard')
    
    return render(request, 'fees/receipt.html', {'payment': payment})

@login_required
def my_fees(request):
    if not request.user.is_student:
        return redirect('dashboard')
    
    payments = FeePayment.objects.filter(student=request.user).order_by('-date')
    return render(request, 'fees/my_fees.html', {'payments': payments})
