from django.shortcuts import render, redirect
from django.contrib.auth import logout
from users.models import User

# Create your views here.

def index_view(request):
    """
    Página Inicial
    """
    data = {}
    if request.user.is_authenticated:
        try:
            data['student'] = request.user.student
            if not hasattr(data['student'], 'is_active') or not data['student'].is_active:
                return redirect('student:student_form')
        except User.student.RelatedObjectDoesNotExist:
            return redirect('student:student_form')
    else:
        data['student'] = None
    return render(request, 'core/index.html', data)

def logout_view(request):
    """
    Página de Logout
    """
    logout(request)
    return render(request, 'core/index.html')
