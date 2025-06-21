# portfolio_analyzer/scorer.py

"""
This module scores the user's portfolio based on a weighted combination of metrics:
- Tech stack diversity
- Project domain diversity
- GitHub stars (reputation)
- README quality (documentation)
"""
import numpy as np
import json

# Define the weights for each scoring component. They should sum to 1.0.
WEIGHTS = {
    "tech_diversity": 0.30,
    "domain_diversity": 0.30,
    "popularity": 0.25,
    "readme_quality": 0.15,
}

def _normalize_score(value, max_value, log_scale=False):
    """
    Normalizes a value to a 0-100 scale.
    Can use a logarithmic scale for values that vary widely, like star counts.
    """
    if max_value == 0:
        return 0
    if log_scale:
        # Add 1 to avoid log(0)
        score = np.log(value + 1) / np.log(max_value + 1)
    else:
        score = value / max_value
    
    return min(score * 100, 100)


def score_portfolio(repos_data, skills):
    """
    Scores the portfolio based on project quality, diversity, and other metrics.

    Args:
        repos_data (list): A list of repository dictionaries from the scraper.
        skills (dict): A dictionary with skill counts from the skill extractor.

    Returns:
        dict: A dictionary containing the final score and the breakdown of sub-scores.
    """
    num_repos = len(repos_data)
    if num_repos == 0:
        return {"total_score": 0, "breakdown": {}}

    # 1. Tech Stack Diversity Score
    # The more unique skills used, the better. Max value is the total number of skills we track.
    num_unique_skills = len(skills)
    # A simple target: 20 unique skills is a strong portfolio.
    tech_diversity_score = _normalize_score(num_unique_skills, 20)

    # 2. Domain Diversity Score
    # The more project clusters, the better.
    clusters = {repo.get('cluster') for repo in repos_data if 'cluster' in repo}
    num_clusters = len(clusters)
    # A simple target: 5 different domains/clusters is a diverse portfolio.
    domain_diversity_score = _normalize_score(num_clusters, 5)

    # 3. Popularity Score (GitHub Stars)
    # Total stars across all repos. Use log scale due to high variability.
    total_stars = sum(repo.get('star_count', 0) for repo in repos_data)
    # A simple target: 100 stars is a great milestone.
    popularity_score = _normalize_score(total_stars, 100, log_scale=True)
    
    # 4. README Quality Score
    # Average length of READMEs. Longer READMEs often mean better documentation.
    readme_lengths = [len(repo.get('readme_content', '')) for repo in repos_data]
    avg_readme_length = sum(readme_lengths) / num_repos if num_repos > 0 else 0
    # A simple target: an average of 1500 characters (a few paragraphs) is good.
    readme_quality_score = _normalize_score(avg_readme_length, 1500)

    # Calculate final weighted score
    final_score = (
        tech_diversity_score * WEIGHTS["tech_diversity"] +
        domain_diversity_score * WEIGHTS["domain_diversity"] +
        popularity_score * WEIGHTS["popularity"] +
        readme_quality_score * WEIGHTS["readme_quality"]
    )

    score_breakdown = {
        "Tech Diversity": tech_diversity_score,
        "Domain Diversity": domain_diversity_score,
        "GitHub Popularity": popularity_score,
        "README Quality": readme_quality_score,
    }
    
    return {
        "total_score": int(final_score),
        "breakdown": score_breakdown
    }

    return scores