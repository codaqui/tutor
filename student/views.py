from django.shortcuts import render, redirect
from .forms import StudentProfileForm
from .models import Student

# Create your views here.

def student_data_form_view(request):
    if request.method == 'POST':
        form = StudentProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:index')
    else:
        form = StudentProfileForm()
    return render(request, 'student/student_form.html', {'form': form})
