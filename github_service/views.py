import logging

import pytest
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from codaqui.settings import GITHUB_ORGANIZATION, GITHUB_REPOSITORY

from github_service.auth import generate_access_token, generate_jwt_from_app
from users.models import User


def github_headers():
    access_token = generate_access_token()
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
    }


def github_user_headers(user: User):
    github_token = user.get_github_token()
    return {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }


def github_headers_with_json():
    jwt_token = generate_jwt_from_app()
    return {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    }


def github_who_am_i():
    """
    Retrieves information about the authenticated GitHub App.

    Returns:
        dict: A dictionary containing information about the GitHub App.

    Raises:
        requests.exceptions.RequestException: If an error occurs while making the API request.
    """
    url = f"https://api.github.com/app"
    headers = github_headers_with_json()
    response = requests.get(url, headers=headers)
    return response.json()


def invite_user_to_github_team(github_username: str):
    """
    Invites a student to join the GitHub Team.

    Args:
        student_id (int): The student's ID.
    """
    logging.info(f"Inviting {github_username} to the GitHub Team")
    url = f"https://api.github.com/orgs/{GITHUB_ORGANIZATION}/teams/intranet/memberships/{github_username}"
    headers = github_headers()
    response = requests.put(url, headers=headers)
    return response

def verify_membership(github_username: str) -> bool:
    """
    Verifies if a user is a member of the GitHub Team.

    Args:
        github_username (str): The GitHub username.

    Returns:
        bool: True if the user is a member of the GitHub Team, False otherwise.
    """
    url = f"https://api.github.com/orgs/{GITHUB_ORGANIZATION}/teams/intranet/memberships/{github_username}"
    headers = github_headers()
    response = requests.get(url, headers=headers)
    return (True if response.status_code == 200 and response.json()["state"] == "active" else False)


def list_issues() -> list:
    """
    List all issues in the GitHub repository.

    Returns:
        list: A list of dictionaries containing information about the issues.
    """
    url = (
        f"https://api.github.com/repos/{GITHUB_ORGANIZATION}/{GITHUB_REPOSITORY}/issues"
    )
    headers = github_headers()
    response = requests.get(url, headers=headers)
    return response.json()


def get_issue(issue_number: int):
    """
    Retrieves information about an issue.

    Args:
        issue_number (int): The issue number.

    Returns:
        dict: A dictionary containing information about the issue.
    """
    url = f"https://api.github.com/repos/{GITHUB_ORGANIZATION}/{GITHUB_REPOSITORY}/issues/{issue_number}"
    headers = github_headers()
    response = requests.get(url, headers=headers)
    return response.json()


def assign_user_issue(issue_number: int, assignee: str):
    """
    Assigns an issue to a user.

    API: https://docs.github.com/pt/rest/issues/issues?apiVersion=2022-11-28#update-an-issue

    Args:
        issue_number (int): The issue number.
        assignee (str): The GitHub username of the assignee.
    """
    url = f"https://api.github.com/repos/{GITHUB_ORGANIZATION}/{GITHUB_REPOSITORY}/issues/{issue_number}"
    headers = github_headers()
    data = {"assignees": [assignee]}
    response = requests.patch(url, headers=headers, json=data)
    return response

def list_comments(issue_number: int) -> list:
    """
    List all comments on an issue.

    Args:
        issue_number (int): The issue number.

    Returns:
        list: A list of dictionaries containing information about the comments.
    """
    url = f"https://api.github.com/repos/{GITHUB_ORGANIZATION}/{GITHUB_REPOSITORY}/issues/{issue_number}/comments"
    headers = github_headers()
    response = requests.get(url, headers=headers)
    return response.json() 

def create_comment(issue_number: int, comment: str, user: User):
    """
    Creates a comment on an issue.

    Args:
        issue_number (int): The issue number.
        comment (str): The comment text.
    """
    url = f"https://api.github.com/repos/{GITHUB_ORGANIZATION}/{GITHUB_REPOSITORY}/issues/{issue_number}/comments"
    headers = github_user_headers(user)
    data = {"body": comment}
    response = requests.post(url, headers=headers, json=data)
    return response   


@login_required
def view_issue_controller(request, issue_number, action):
    valid_actions = ["view", "auto_assigne"]
    if action == "view":
        issue = get_issue(issue_number)
        logging.info(f"Found issue: {issue}")
        logging.info(f"Issue Fields: {issue.keys()}")
        return render(request, "github_service/view_issue.html", {"issue": issue})
    elif action == "auto_assigne":
        user_action: User = request.user
        assignee = user_action.get_github_username()
        response = assign_user_issue(issue_number, assignee)
        if response.status_code == 200:
            return redirect("github_service:issue_controller", issue_number, "view")
        else:
            logging.error(f"Error assigning issue #{issue_number} to {assignee}")
            logging.error(f"Response: {response.json()}")
            message = f"Failed to assign issue #{issue_number} to {assignee}!"
            error_code = 500
            return render(
                request, "utils/error.html", {"message": message}, status=error_code
            )
    else:
        message = f"Invalid action: {action}, valid actions are: {valid_actions}!"
        error_code = 400
        return render(
            request, "utils/error.html", {"message": message}, status=error_code
        )


@login_required
def view_issue_list(request):
    issues = list_issues()
    issues_len = len(issues)
    logging.info(f"Found {len(issues)} issues")
    if issues_len > 0:
        logging.info(f"Issues Keys: {issues[0].keys()}")
    else:
        logging.info("No issues found")
    return render(request, "github_service/list_issues.html", {"issues": issues})

@login_required
def view_issue_comment_controller(request, issue_number):
    if request.method == "POST":
        comment = request.POST.get("comment")
        response = create_comment(issue_number, comment, request.user)
        if response.status_code == 201:
            return redirect("github_service:issue_comments_controller", issue_number=issue_number)
        else:
            logging.error(f"Error creating comment on issue #{issue_number}")
            logging.error(f"Response: {response.json()}")
            message = f"Failed to create comment on issue #{issue_number}!"
            error_code = 500
            return render(
                request, "utils/error.html", {"message": message}, status=error_code
            )

    comments = list_comments(issue_number)
    return render(
        request,
        "github_service/comments_issue.html",
        {"comments": comments, "issue_number": issue_number},
    )