# portfolio_analyzer/skills_extractor.py

"""
This module extracts tech skills and keywords from project descriptions and READMEs.
It uses a predefined list of skills and regex to find matches in the text.
"""
import re
from collections import Counter
import json

# A curated list of data science and software engineering skills.
# The keys are the canonical skill names.
# The values are lists of regex patterns to match different aliases or formats.
SKILL_KEYWORDS = {
    "Python": [r"\bpython\b"],
    "R": [r"\br\b"],
    "SQL": [r"\bsql\b"],
    "Java": [r"\bjava\b"],
    "C++": [r"\bc\+\+\b"],
    "JavaScript": [r"\bjavascript\b"],
    "HTML": [r"\bhtml\b"],
    "CSS": [r"\bcss\b"],
    "Bash": [r"\bbash\b"],
    "Scala": [r"\bscala\b"],
    "Julia": [r"\bjulia\b"],
    "Pandas": [r"\bpandas\b"],
    "NumPy": [r"\bnumpy\b"],
    "Scikit-learn": [r"\bscikit-learn\b", r"\bsklearn\b"],
    "SciPy": [r"\bscipy\b"],
    "Matplotlib": [r"\bmatplotlib\b"],
    "Seaborn": [r"\bseaborn\b"],
    "Plotly": [r"\bplotly\b"],
    "TensorFlow": [r"\btensorflow\b"],
    "PyTorch": [r"\bpytorch\b"],
    "Keras": [r"\bkeras\b"],
    "spaCy": [r"\bspacy\b"],
    "NLTK": [r"\bnltk\b"],
    "Gensim": [r"\bgensim\b"],
    "Transformers": [r"\btransformers\b"],
    "Hugging Face": [r"\bhugging face\b", r"\bhuggingface\b"],
    "Spark": [r"\bspark\b", r"\bpyspark\b"],
    "Hadoop": [r"\bhadoop\b"],
    "Kafka": [r"\bkafka\b"],
    "Airflow": [r"\bairflow\b"],
    "Docker": [r"\bdocker\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "Git": [r"\bgit\b"],
    "Flask": [r"\bflask\b"],
    "Django": [r"\bdjango\b"],
    "Streamlit": [r"\bstreamlit\b"],
    "Dash": [r"\bdash\b"],
    "FastAPI": [r"\bfastapi\b"],
    "AWS": [r"\baws\b", r"\bamazon web services\b"],
    "GCP": [r"\bgcp\b", r"\bgoogle cloud platform\b"],
    "Azure": [r"\bazure\b"],
    "MongoDB": [r"\bmongodb\b"],
    "PostgreSQL": [r"\bpostgresql\b", r"\bpostgres\b"],
    "MySQL": [r"\bmysql\b"],
    "Redis": [r"\bredis\b"],
    "Elasticsearch": [r"\belasticsearch\b"],
    "Tableau": [r"\btableau\b"],
    "Power BI": [r"\bpower bi\b"],
}


def extract_skills(repos_data):
    """
    Extracts skills from the text of all repositories using regex matching.

    Args:
        repos_data (list): A list of repository dictionaries from the github_scraper.

    Returns:
        tuple: A tuple containing:
            - collections.Counter: A frequency count of each skill across all projects.
            - dict: A dictionary mapping each repo name to a set of its skills.
    """
    overall_skill_counts = Counter()
    repo_skills = {}

    for repo in repos_data:
        repo_name = repo["name"]
        repo_skills[repo_name] = set()
        
        # Combine description and README for a comprehensive text source
        text_content = (repo.get("description", "") + " " + repo.get("readme_content", "")).lower()
        
        if not text_content.strip():
            continue

        for skill, patterns in SKILL_KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, text_content, re.IGNORECASE):
                    if skill not in repo_skills[repo_name]:
                        overall_skill_counts[skill] += 1
                    repo_skills[repo_name].add(skill)

    return overall_skill_counts, repo_skills 