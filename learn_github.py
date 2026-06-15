import os
from github import Github, Auth

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")


auth = Auth.Token(GITHUB_TOKEN)
g = Github(auth=auth)

def get_pr_diff(repo_name, pr_number):
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    print(f"PR Title: {pr.title}")
    print(f"PR Author: {pr.user.login}")
    print(f"Files changed: {pr.changed_files}")
    print("---")

    full_diff = ""

    for file in pr.get_files():
        full_diff += f"\nFile: {file.filename}\n"
        full_diff += f"Changes: +{file.additions} added, -{file.deletions} deleted\n"
        
        if file.patch:
            full_diff += file.patch
        
        full_diff += "\n"

    return full_diff

diff = get_pr_diff("Piya-1803/test_repo", 2)
print(diff[:2000])