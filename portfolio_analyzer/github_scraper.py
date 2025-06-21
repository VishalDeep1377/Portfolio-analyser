# portfolio_analyzer/github_scraper.py

"""
This module fetches GitHub data for a given user using the PyGithub library.
"""
import os
from github import Github, GithubException
import streamlit as st

@st.cache_data(ttl=3600) # Cache data for 1 hour
def get_user_repos(username, github_token=None):
    """
    Fetches, filters, and processes public repositories for a given GitHub user.

    Args:
        username (str): The GitHub username.
        github_token (str, optional): A GitHub personal access token to increase API rate limits.
                                      If not provided, it will check for a GITHUB_TOKEN environment variable.

    Returns:
        list: A list of dictionaries, where each dictionary represents a repository
              and contains its name, description, language, stars, and README content.
              Returns an empty list if the user is not found or has no valid repositories.
    """
    if not github_token:
        github_token = os.environ.get("GITHUB_TOKEN")

    g = Github(github_token)

    try:
        user = g.get_user(username)
    except GithubException:
        print(f"Error: User '{username}' not found.")
        return []

    processed_repos = []
    for repo in user.get_repos():
        # Filter out forked repositories
        if repo.fork:
            continue

        # Get README content
        readme_content = ""
        try:
            readme_file = repo.get_readme()
            readme_content = readme_file.decoded_content.decode("utf-8")
        except GithubException:
            # This exception is caught if the repo has no README
            pass

        # Filter out empty repos (no description and no README)
        if not repo.description and not readme_content:
            continue

        repo_data = {
            "name": repo.name,
            "description": repo.description or "",
            "primary_language": repo.language or "Not specified",
            "star_count": repo.stargazers_count,
            "readme_content": readme_content,
            "commits": []
        }

        # Get commit activity (this can be slow, so caching is crucial)
        try:
            for commit in repo.get_commits():
                repo_data["commits"].append(commit.commit.author.date)
        except GithubException:
            pass # Handle cases where commits are not accessible

        processed_repos.append(repo_data)

    return processed_repos 