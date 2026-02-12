import git
import os
import shutil

class GitOps:
    def __init__(self, work_dir="./temp_repos"):
        self.work_dir = work_dir
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)

    def clone_repo(self, repo_url, repo_dir):
        repo_path = os.path.join(self.work_dir, repo_dir)
        if os.path.exists(repo_path):
            # Windows workaround for read-only git files
            def on_rm_error(func, path, exc_info):
                import stat
                try:
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                except Exception as e:
                    print(f"Failed to remove {path}: {e}")
            
            shutil.rmtree(repo_path, onerror=on_rm_error)
        
        print(f"Cloning {repo_url} to {repo_path}...")
        repo = git.Repo.clone_from(repo_url, repo_path)
        return repo, repo_path

    def checkout_branch(self, repo, branch_name):
        print(f"Checking out {branch_name}...")
        repo.git.checkout(branch_name)

    def commit_and_push(self, repo, files_to_add, commit_message, branch_name):
        print(f"Committing changes: {files_to_add}")
        repo.index.add(files_to_add)
        repo.index.commit(commit_message)
        print(f"Pushing to origin/{branch_name}...")
        origin = repo.remote(name='origin')
        origin.push(branch_name)
