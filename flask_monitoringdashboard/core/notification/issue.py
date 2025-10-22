import requests
from GithubRequestInfo import GitHubRequestInfo 


def get_base_repo_url(repo_owner:str, repo_name:str):
    return f"https://api.github.com/repos/{repo_owner}/{repo_name}/"    

def get_issue_url(repo_owner: str, repo_name: str):
    return get_base_repo_url(repo_owner, repo_name) + "issues"

def get_endpoint_url(repo_owner: str, repo_name: str, endpoint: str):
        return f"https://api.github.com/repos/{repo_owner}/{repo_name}/{endpoint}"

def make_post_request(request_info: GitHubRequestInfo, data):
   url = get_endpoint_url(request_info.repo_owner, request_info.repo_name, request_info.endpoint)
   headers = post_headers(request_info.github_token)

   return requests.post(url, headers=headers, json=data)

def make_get_request(request_info: GitHubRequestInfo) -> requests.Response:
    # Get the URL for the repository
    url = get_endpoint_url(request_info.repo_owner, request_info.repo_name, request_info.endpoint)
    
    # Get headers and params
    headers = get_headers(request_info.github_token) # Get headers with token
    params = get_params() # Get defailt params
    
    # Make the request and return the response as a request.Response object
    return requests.get(url, headers=headers, params=params)

def get_params():
    params = { 
        "state": "all",  # Get only open pull requests
    }
    return params


def get_headers(github_token: str):
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    return headers

def post_headers(github_token:str):
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3.raw+json"
    }
    return headers

def main():
    print("This is a utility file with helper functions not to be run directly.")

if __name__ == "__main__":
    main()