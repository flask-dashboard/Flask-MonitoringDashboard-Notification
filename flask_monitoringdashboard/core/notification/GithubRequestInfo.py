class GitHubRequestInfo:
    """
    RequestInfo is a class that represents the information of a request.
    """

    def __init__(self, github_token: str, repo_owner: str, repo_name: str):
        """
        Initializes the RequestInfo object with the given parameters.

        :param github_token: the PAT token that has access to the repository
        :param repo_owner: The owner/organistation that contains the repository
        :param repo_name: The name of the repository
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token