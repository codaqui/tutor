import requests
from github_service.auth import generate_access_token, generate_jwt_from_app


def github_headers():
    access_token = generate_access_token()
    return {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/vnd.github+json'
    }

def github_headers_with_json():
    jwt_token = generate_jwt_from_app()
    return {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json'
    }

def github_who_am_i():
    """
    Retrieves information about the authenticated GitHub App.

    Returns:
        dict: A dictionary containing information about the GitHub App.

    Raises:
        requests.exceptions.RequestException: If an error occurs while making the API request.
    """
    url = f'https://api.github.com/app'
    headers = github_headers_with_json()
    response = requests.get(url, headers=headers)
    return response.json()


def invite_user_to_github_team(github_username: str):
    """
    Invites a student to join the GitHub Team.

    Args:
        student_id (int): The student's ID.
    """
    url = f'https://api.github.com/orgs/codaqui/teams/intranet/memberships/{github_username}'
    headers = github_headers()
    response = requests.put(url, headers=headers)
    return response

def verify_membership(github_username: str):
    """
    Verifies if a user is a member of the GitHub Team.

    Args:
        github_username (str): The GitHub username.

    Returns:
        bool: True if the user is a member of the GitHub Team, False otherwise.
    """
    url = f'https://api.github.com/orgs/codaqui/teams/intranet/memberships/{github_username}'
    headers = github_headers()
    response = requests.get(url, headers=headers)
    return response.status_code == 200
