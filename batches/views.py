from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Batch
from .forms import BatchForm

def is_teacher(user):
    return user.is_authenticated and user.is_teacher

@login_required
@user_passes_test(is_teacher)
def batch_list(request):
    batches = Batch.objects.all()
    return render(request, 'batches/batch_list.html', {'batches': batches})

@login_required
@user_passes_test(is_teacher)
def batch_create(request):
    if request.method == 'POST':
        form = BatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Batch created successfully.')
            return redirect('batch_list')
    else:
        form = BatchForm()
    return render(request, 'batches/batch_form.html', {'form': form})

@login_required
@user_passes_test(is_teacher)
def batch_update(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == 'POST':
        form = BatchForm(request.POST, instance=batch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Batch updated successfully.')
            return redirect('batch_list')
    else:
        form = BatchForm(instance=batch)
    return render(request, 'batches/batch_form.html', {'form': form, 'is_update': True})

@login_required
@user_passes_test(is_teacher)
def batch_delete(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == 'POST':
        batch.delete()
        messages.success(request, 'Batch deleted successfully.')
        return redirect('batch_list')
    return render(request, 'batches/batch_confirm_delete.html', {'batch': batch})
