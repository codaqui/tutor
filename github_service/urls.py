"""
URL configuration for codaqui project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from github_service.apps import GithubServiceConfig
from github_service.views import (
    view_issue_controller,
    view_issue_list,
    view_issue_comment_controller,
)

app_name = GithubServiceConfig.name

urlpatterns = [
    path("list-issues/", view_issue_list, name="list_issues"),
    path(
        "issue/<int:issue_number>/<str:action>/",
        view_issue_controller,
        name="issue_controller",
    ),
    path(
        "issue/comments/<int:issue_number>/",
        view_issue_comment_controller,
        name="issue_comments_controller",
    ),
]
