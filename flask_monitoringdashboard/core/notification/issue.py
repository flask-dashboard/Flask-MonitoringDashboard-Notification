import requests
from flask_monitoringdashboard.core.notification.notification_content import NotificationContent
from .GithubRequestInfo import GitHubRequestInfo 


def get_base_repo_url(repo_owner:str, repo_name:str):
    return f"https://api.github.com/repos/{repo_owner}/{repo_name}/"    

def get_issue_url(repo_owner: str, repo_name: str):
    return get_base_repo_url(repo_owner, repo_name) + "issues"

def get_endpoint_url(repo_owner: str, repo_name: str, endpoint: str):
        return f"https://api.github.com/repos/{repo_owner}/{repo_name}/{endpoint}"

def make_post_request(request_info: GitHubRequestInfo, endpoint: str, data):
   url = get_endpoint_url(request_info.repo_owner, request_info.repo_name, endpoint)
   headers = _post_headers(request_info.github_token)

   return requests.post(url, headers=headers, json=data)

def create_issue(
        request_info: GitHubRequestInfo,
        notification_content: NotificationContent) -> requests.Response:
    print("this is the body:", notification_content.body_markdown)
    data = {
        "title": notification_content.title,
        "body": notification_content.body_markdown,
        "labels": ["automated-issue", "exception"], 
    }

    return make_post_request(request_info, "issues", data)

def _post_headers(github_token:str):
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    return headers

def main():
    print("This is a utility file with helper functions not to be run directly.")

if __name__ == "__main__":
    main()