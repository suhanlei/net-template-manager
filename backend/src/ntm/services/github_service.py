import logging
from github import Github, GithubException
from github.Repository import Repository

from ntm.core.config import get_settings

logger = logging.getLogger(__name__)

_settings = None


def _get_settings():
    global _settings
    if _settings is None:
        _settings = get_settings()
    return _settings


def _get_client() -> Github:
    s = _get_settings()
    return Github(s.github_token)


def _get_repo(client: Github) -> Repository | None:
    s = _get_settings()
    if not s.github_repo:
        return None
    try:
        return client.get_repo(s.github_repo)
    except GithubException as e:
        logger.error(f"Failed to get repo {s.github_repo}: {e}")
        return None


def test_connection() -> dict:
    """Test GitHub token and repo access."""
    s = _get_settings()
    if not s.github_token:
        return {"connected": False, "error": "No GITHUB_TOKEN configured"}

    try:
        client = _get_client()
        user = client.get_user()
        info = {"connected": True, "user": user.login}

        repo = _get_repo(client)
        if repo:
            info["repo"] = repo.full_name
            info["branch"] = repo.default_branch
            info["private"] = repo.private
        else:
            info["repo_error"] = f"Cannot access {s.github_repo}"

        return info
    except GithubException as e:
        return {"connected": False, "error": str(e)}


def get_repo_info() -> dict | None:
    """Get repository metadata."""
    client = _get_client()
    repo = _get_repo(client)
    if not repo:
        return None
    return {
        "full_name": repo.full_name,
        "description": repo.description,
        "default_branch": repo.default_branch,
        "private": repo.private,
        "html_url": repo.html_url,
    }


def commit_file(path: str, content: str, message: str, branch: str | None = None) -> dict:
    """Create or update a file in the repository. Returns commit info."""
    s = _get_settings()
    client = _get_client()
    repo = _get_repo(client)
    if not repo:
        return {"success": False, "error": "Repository not accessible"}

    branch = branch or s.github_branch
    max_retries = 3

    for attempt in range(max_retries):
        try:
            # Try to get existing file
            try:
                existing = repo.get_contents(path, ref=branch)
                sha = existing.sha
                result = repo.update_file(path, message, content, sha, branch=branch)
            except GithubException as e:
                if e.status == 404:
                    # File doesn't exist, create it
                    result = repo.create_file(path, message, content, branch=branch)
                else:
                    raise

            return {
                "success": True,
                "commit_sha": result["commit"].sha,
                "action": "update" if attempt == 0 and "existing" in dir() else "create",
            }
        except GithubException as e:
            if e.status == 422 and attempt < max_retries - 1:
                # SHA conflict — retry
                logger.warning(f"SHA conflict on attempt {attempt + 1}, retrying...")
                continue
            return {"success": False, "error": str(e)}

    return {"success": False, "error": "Max retries exceeded due to SHA conflicts"}


def create_tag(version: str, branch: str | None = None) -> dict:
    """Create a git tag for a release."""
    s = _get_settings()
    client = _get_client()
    repo = _get_repo(client)
    if not repo:
        return {"success": False, "error": "Repository not accessible"}

    branch = branch or s.github_branch
    try:
        # Get branch HEAD
        ref = repo.get_git_ref(f"heads/{branch}")
        commit_sha = ref.object.sha

        # Create tag reference
        tag_ref = f"tags/v{version}"
        repo.create_git_ref(f"refs/{tag_ref}", sha=commit_sha)

        return {"success": True, "tag": f"v{version}", "sha": commit_sha}
    except GithubException as e:
        return {"success": False, "error": str(e)}


def create_release(version: str, name: str, body: str, branch: str | None = None) -> dict:
    """Create a GitHub Release."""
    s = _get_settings()
    client = _get_client()
    repo = _get_repo(client)
    if not repo:
        return {"success": False, "error": "Repository not accessible"}

    tag = f"v{version}"
    try:
        release = repo.create_git_release(tag, name, body, draft=False)
        return {
            "success": True,
            "tag": tag,
            "release_url": release.html_url,
            "release_id": release.id,
        }
    except GithubException as e:
        return {"success": False, "error": str(e)}


def sync_recent_commits(since: str | None = None) -> dict:
    """Fetch recent commits from GitHub and return summary."""
    s = _get_settings()
    client = _get_client()
    repo = _get_repo(client)
    if not repo:
        return {"success": False, "error": "Repository not accessible"}

    try:
        kwargs = {}
        if since:
            from datetime import datetime
            kwargs["since"] = datetime.fromisoformat(since)

        commits = repo.get_commits(sha=s.github_branch, **kwargs)
        commit_list = []
        for c in commits[:50]:  # Limit to 50
            commit_list.append({
                "sha": c.sha,
                "message": c.commit.message,
                "author": c.commit.author.name,
                "date": c.commit.author.date.isoformat(),
            })

        return {"success": True, "commits": commit_list, "count": len(commit_list)}
    except GithubException as e:
        return {"success": False, "error": str(e)}
