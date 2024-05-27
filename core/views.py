from django.shortcuts import render
from django.contrib.auth import logout
from users.models import User

# Create your views here.

def index_view(request):
    """
    Página Inicial
    """
    data = {}
    try:
        data['student'] = request.user.student
    except User.student.RelatedObjectDoesNotExist:
        data['student'] = None
    return render(request, 'core/index.html', data)

def logout_view(request):
    """
    Página de Logout
    """
    logout(request)
    return render(request, 'core/index.html')