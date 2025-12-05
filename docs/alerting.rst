Alerting
=============

Creating issues on GitHub
--------------------------
You can configure FMD to create GitHub issues automatically when an exception occurs.
To enable this feature, you need to set the following configuration options:

.. code-block:: python

   [alerting]
   ENABLED=True
   TYPE=issue
   GITHUB_TOKEN=<example_github_token>
   REPOSITORY_OWNER=<example_repo_owner>
   REPOSITORY_NAME=<example_repo_name>


Steps to generate the needed GitHub access token:

1. Go to https://github.com.
2. Log in to the account.
3. Click on the profile and go to settings.
4. Click on ”Developer Settings”.
5. On the left sidebar under ”Personal access token”, click ”Fine-grained tokens” and then click ”Create new token”.
6. Under Token name, enter a name for the token.
7. Under Expiration, select an expiration for the token.
8. Optionally, under Description, add a note to describe the purpose of the token.
9. Under Resource owner, select the resource owner. (Here an organization could also be chosen. Should be the same as REPO OWNER.)
10. Under Repository access, select which repositories the token should access. (Select the same as REPO NAME.)
11.  Under Permissions, select which permissions to grant the token. (Select ”Issues” and then ”read and write”.)
12. Click ”Generate token”. (Remember to copy the GITHUB TOKEN.)
13. In the Config.cfg provide the following:
14. REPO OWNER
15. REPO NAME
16. GITHUB TOKEN

A guide to create GitHub access tokens can also be found here:
https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens