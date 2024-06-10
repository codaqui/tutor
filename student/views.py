from django.shortcuts import render, redirect
from student.forms import StudentProfileForm
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def student_data_form_view(request):
    if request.method == 'POST':
        form = StudentProfileForm(request.POST)
        # TODO - Criar um espaço somente para atualizar cadastro no futuro.
        if request.user.student:
            form = StudentProfileForm(request.POST, instance=request.user.student)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('core:index')
    else:
        if request.user.student:
            form = StudentProfileForm(instance=request.user.student)
        else:
            form = StudentProfileForm()
    return render(request, 'student/student_form.html', {'form': form})
