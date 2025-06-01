from git import Repo, GitCommandError
import os

def sync_with_github(repo_path, filename="user_feedback.csv"):
    try:
        repo = Repo(repo_path)
        origin = repo.remotes.origin
        origin.pull()

        file_path = os.path.join(repo_path, filename)
        if os.path.exists(file_path):
            repo.git.add(file_path)
            if repo.is_dirty():
                repo.index.commit("📝 Add/update feedback")
                origin.push()
                print("✅ GitHub sync complete.")
            else:
                print("ℹ️ No changes to commit.")
        else:
            print(f"⚠️ File not found: {file_path}")

    except GitCommandError as e:
        print(f"❌ Git error: {e}")
    except Exception as e:
        print(f"❌ General error: {e}")

def pull_only(repo_path):
    try:
        repo = Repo(repo_path)
        origin = repo.remotes.origin
        origin.pull()
        print("🔄 Pulled latest from GitHub.")
    except Exception as e:
        print(f"❌ Pull failed: {e}")
