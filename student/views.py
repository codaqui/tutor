from django.shortcuts import render, redirect
from utils.models import get_or_none
from student.forms import StudentProfileForm
from student.models import Student
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def student_data_form_view(request):
    data = {}
    student = get_or_none(Student, user=request.user)


    # Request == POST
    if request.method == 'POST':
        if not student:
            form = StudentProfileForm(request.POST)
        else:
            form = StudentProfileForm(request.POST, instance=request.user.student)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('core:index')
        else:
            raise ValueError(form.errors)
        
    # Request == GET
    elif request.method == 'GET':
        if student:
            form = StudentProfileForm(instance=request.user.student)
        else:
            form = StudentProfileForm()
        data['form'] = form
        return render(request, 'student/student_form.html', data)
    
    # Other Request
    else:
        return redirect('core:index')
