# portfolio_analyzer/recommender.py

"""
This module generates recommendations based on a rule-based system.
It identifies skill gaps and suggests new projects and learning resources
without relying on a paid LLM API.
"""
import random
import re
from summarizer import generate_summary

# A predefined list of core data science skills and domains.
CORE_SKILLS = {
    "Data Analysis": ["Python", "Pandas", "NumPy", "Matplotlib", "Seaborn"],
    "Machine Learning": ["Scikit-learn", "TensorFlow", "PyTorch", "Keras"],
    "Big Data": ["Spark", "Hadoop", "Kafka"],
    "Databases": ["SQL", "PostgreSQL", "MySQL", "MongoDB"],
    "Web Development/Deployment": ["Flask", "Django", "Docker", "AWS", "Streamlit"],
    "NLP": ["NLTK", "spaCy", "Hugging Face", "Gensim"]
}

# A mapping of domains to project ideas.
PROJECT_IDEAS = {
    "Data Analysis": "Develop an interactive sales dashboard using Plotly.",
    "Machine Learning": "Build a classification model to predict customer churn.",
    "Big Data": "Create a data pipeline to process real-time streaming data with Spark.",
    "Databases": "Design and implement a relational database for an e-commerce site.",
    "Web Development/Deployment": "Containerize a machine learning app with Docker and deploy it.",
    "NLP": "Perform sentiment analysis on product reviews using Hugging Face transformers."
}

# A mapping of skills to example learning resources.
COURSE_SUGGESTIONS = {
    "Pandas": "https://www.coursera.org/learn/python-data-analysis",
    "Scikit-learn": "https://www.coursera.org/learn/machine-learning-with-python",
    "Spark": "https://www.udemy.com/course/spark-and-python-for-big-data-with-pyspark/",
    "SQL": "https://www.coursera.org/learn/sql-for-data-science",
    "Docker": "https://www.udemy.com/course/docker-for-the-absolute-beginner/",
    "NLP": "https://www.coursera.org/learn/natural-language-processing-specialization"
}

# A knowledge base mapping job roles to their ideal skill sets.
TARGET_JOB_SKILLS = {
    "Data Analyst": {
        "Core": ["SQL", "Tableau", "Power BI", "Python", "Pandas"],
        "Secondary": ["Excel", "Statistics", "Communication"]
    },
    "Data Scientist": {
        "Core": ["Python", "Scikit-learn", "TensorFlow", "PyTorch", "SQL", "Pandas", "Statistics"],
        "Secondary": ["Spark", "AWS", "Docker", "Communication"]
    },
    "Machine Learning Engineer": {
        "Core": ["Python", "TensorFlow", "PyTorch", "Docker", "Kubernetes", "AWS", "SQL"],
        "Secondary": ["C++", "Java", "MLflow", "Airflow"]
    },
    "Data Engineer": {
        "Core": ["SQL", "Python", "Spark", "Kafka", "Airflow", "AWS", "Hadoop"],
        "Secondary": ["Scala", "Java", "Docker", "Kubernetes"]
    }
}

def generate_linkedin_recommendations(linkedin_data):
    """
    Analyzes LinkedIn data and provides AI-powered, contextual recommendations.

    Args:
        linkedin_data (dict): The parsed data from a LinkedIn profile.

    Returns:
        list: A list of string recommendations.
    """
    recommendations = []
    
    # 1. Analyze the professional summary
    summary = linkedin_data.get("summary", "").strip()
    if not summary:
        recommendations.append("Add a professional summary to give visitors a clear overview of your background and goals.")
    else:
        prompt = f"Instruction: Review the following professional summary. Provide one concise, actionable suggestion for improvement, focusing on active language and highlighting key skills. Do not just say 'add skills'. Summary: \"{summary}\"\n\nSuggestion:"
        suggestion = generate_summary(prompt)
        if "unavailable" not in suggestion.lower() and len(suggestion) > 10:
            recommendations.append(suggestion)

    # 2. Analyze the most recent job experience for impact
    experience = linkedin_data.get("experience", [])
    if experience:
        most_recent_job = experience[0]
        description = most_recent_job.get("description", "")
        if not description:
            recommendations.append(f"Add a description for your role as '{most_recent_job['title']}' to detail your responsibilities and achievements.")
        else:
            prompt = f"Instruction: Review the following job description. Does it use strong action verbs and include measurable results? Provide one specific improvement. Description: \"{description}\"\n\nSuggestion:"
            suggestion = generate_summary(prompt)
            if "unavailable" not in suggestion.lower() and len(suggestion) > 10:
                recommendations.append(suggestion)
    else:
        recommendations.append("Add your work experience to build credibility and showcase your professional history.")
        
    # 3. Check for skills
    if len(linkedin_data.get("skills", [])) < 10:
        recommendations.append("Expand your skills section. Aim to list at least 10-15 relevant skills to improve your profile's visibility in searches.")

    if not recommendations:
        return ["Your LinkedIn profile looks solid and covers all key sections!"]
        
    return recommendations

def generate_recommendations(repos_data, skills):
    """
    Generates learning and project recommendations based on skill gaps.

    Args:
        repos_data (list): A list of repository dictionaries.
        skills (dict): A dictionary of the user's detected skills.

    Returns:
        dict: A dictionary containing project ideas, skills to learn, and course suggestions.
    """
    user_skills = set(skills.keys())
    
    # --- Identify Skill Gaps ---
    missing_skills = {}
    for domain, skill_list in CORE_SKILLS.items():
        found_in_domain = any(skill in user_skills for skill in skill_list)
        if not found_in_domain:
            # Recommend the first (most foundational) skill from the missing domain
            missing_skills[domain] = skill_list[0]

    # --- Generate Recommendations ---
    skills_to_learn = list(missing_skills.values())
    
    project_ideas_list = [
        PROJECT_IDEAS[domain] for domain in missing_skills.keys()
        if domain in PROJECT_IDEAS
    ]
    
    # Shuffle to make recommendations feel more dynamic
    random.shuffle(project_ideas_list)
    
    suggested_courses = {
        skill: COURSE_SUGGESTIONS[skill] for skill in skills_to_learn 
        if skill in COURSE_SUGGESTIONS
    }

    # Format project ideas into a single string
    project_ideas_str = "\n".join(f"- {idea}" for idea in project_ideas_list[:3]) # Limit to 3 ideas
    if not project_ideas_str:
        project_ideas_str = "Your portfolio covers a wide range of domains! Consider specializing further in an area you enjoy."

    return {
        "project_ideas": project_ideas_str,
        "skills_to_learn": skills_to_learn[:3], # Limit to 3 skills
        "suggested_courses": suggested_courses
    }