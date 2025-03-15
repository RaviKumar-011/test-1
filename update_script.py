import os
import tempfile
from git import Repo, Actor
import shutil

def clone_repo(repo_url, branch='main'):
    temp_dir = tempfile.mkdtemp()
    repo = Repo.clone_from(repo_url, temp_dir, branch=branch)
    return temp_dir, repo

def read_input_file(repo_path, input_file_path):
    full_path = os.path.join(repo_path, input_file_path)
    if os.path.exists(full_path):
        try:
            with open(full_path, 'r') as input_file:
                return input_file.read().strip()
        except Exception as e:
            print(f"Error reading input file: {e}")
            return None
    else:
        print(f"Input file not found: {full_path}")
        return None

def write_file(repo_path, file_path, content):
    full_path = os.path.join(repo_path, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    try:
        with open(full_path, 'w') as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

def create_and_commit_branch(repo, file_path, new_content, branch_name, commit_message, author_name, author_email):
    new_branch = repo.create_head(branch_name)
    new_branch.checkout()

    if write_file(repo.working_dir, file_path, new_content):
        repo.git.add(file_path)
        author = Actor(author_name, author_email)
        repo.index.commit(commit_message, author=author, committer=author)
        print(f"Committed changes to branch '{branch_name}'.")
        return True
    else:
        return False

def push_branch(repo, branch_name, repo_url, github_token):
    try:
        if repo_url.startswith("https://"):
            parts = repo_url.split("://")
            if len(parts) == 2:
                base_url = parts[1]
                remote_url = f"https://x-access-token:{github_token}@{base_url}"
            else:
                raise ValueError(f"Invalid repo URL: {repo_url}")
        elif repo_url.startswith("git@github.com:"):
            remote_url = f"https://x-access-token:{github_token}@github.com/{repo_url.split('git@github.com:')[1]}"
        else:
            raise ValueError(f"Invalid repo URL: {repo_url}")

        print(f"Remote URL: {remote_url}")
        repo.git.push("--set-upstream", remote_url, branch_name)
        print(f"Pushed branch '{branch_name}' to remote.")
        return True
    except Exception as e:
        print(f"Error pushing branch: {e}")
        return False

if __name__ == "__main__":
    repo_url = "https://github.com/RaviKumar-011/test-1"
    input_file_path = "input/input123.txt"
    branch_name = "feature/update-input"
    commit_message = "Update input file content"
    author_name = "GitHub Actions"
    author_email = "actions@github.com"
    new_content = "ravitest1"

    repo_path, repo = clone_repo(repo_url, branch='main')

    input_text_file = read_input_file(repo_path, input_file_path)

    if not input_text_file:
        exit()

    actual_file_path = read_input_file(repo_path, input_file_path)

    if not actual_file_path:
        exit()

    if create_and_commit_branch(repo, actual_file_path, new_content, branch_name, commit_message, author_name, author_email):
        if push_branch(repo, branch_name, repo_url, os.environ.get('GITHUB_TOKEN')):
            print(f"Successfully modified, committed and pushed branch '{branch_name}'.")
        else:
            print(f"Failed to push branch '{branch_name}'.")
    else:
        print("Failed to modify and commit file.")
