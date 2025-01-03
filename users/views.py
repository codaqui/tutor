from django.shortcuts import render, redirect
from utils.models import get_or_none
from django.contrib.auth.decorators import login_required
from users.models import User
from github_service.views import create_github_repository


@login_required
def user_create_repository(request):

    github_data = request.user.get_github_username()
    create_github_repository(github_data)

    return redirect("core:index")
