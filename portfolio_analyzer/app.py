# portfolio_analyzer/app.py

"""
This module contains the Streamlit frontend for the AI-powered Data Science Portfolio Analyzer.
It orchestrates the backend modules to fetch, analyze, and display portfolio insights
using only free and local resources.
"""

import sys
import os

# Ensure the virtual environment's site-packages is in the path
# This is a robust way to fix ModuleNotFoundError in complex environments
venv_path = os.path.join(os.path.dirname(__file__), '..', 'venv', 'Lib', 'site-packages')
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import your backend modules
from github_scraper import get_user_repos
from skills_extractor import extract_skills
from cluster_projects import cluster_projects
from scorer import score_portfolio
from recommender import generate_recommendations, TARGET_JOB_SKILLS, generate_linkedin_recommendations
from summarizer import generate_summary, generate_readme_summary
from report_generator import generate_pdf_report
from linkedin_parser import parse_linkedin_profile, parse_linkedin_pdf

st.set_page_config(page_title="Data Science Portfolio Analyzer", layout="wide")

def main():
    """
    The main function that runs the Streamlit app.
    """
    st.title("🚀 Professional Data Science Portfolio Analyzer")
    st.write(
        "Enter a GitHub username to evaluate their portfolio, detect skills, "
        "and receive personalized, AI-powered feedback—all using local, open-source models."
    )
    
    with st.sidebar:
        st.header("Analyze a Portfolio")
        st.header("Analyze GitHub Portfolio")
        github_username = st.text_input("GitHub Username", key="username_input", value=st.session_state.get('username', ''))
        github_token = st.text_input("GitHub Personal Access Token", type="password", help="A token with 'public_repo' scope is required to avoid rate limits.")
        github_button = st.button("Analyze GitHub Portfolio", type="primary")

        with st.expander("How to get a GitHub Token"):
            st.markdown("""
            1. **Go to GitHub -> Settings** -> **Developer settings**.
            2. **Personal access tokens** -> **Tokens (classic)**.
            3. **Generate new token** (classic).
            4. **Select `public_repo` scope**. This is the only permission needed.
            5. **Generate token** and copy it here.
            """)
        
        st.divider()
        st.header("Analyze LinkedIn Profile")
        linkedin_file = st.file_uploader("Upload your LinkedIn Profile (HTML or PDF)", type=["html", "htm", "pdf"])
        
        with st.expander("How to download your LinkedIn profile"):
            st.markdown("""
            1. Go to your LinkedIn profile page.
            2. Click the **"More"** button below your profile picture.
            3. Select **"Save to PDF"** from the dropdown menu.
            4. Upload the downloaded PDF file here.
            """)

        linkedin_button = st.button("Analyze LinkedIn Profile")

        st.divider()
        st.sidebar.info("Developed by Vishal Deep")

    # --- GitHub Analysis Logic ---
    if github_button and github_username and github_token:
        st.session_state['analysis_type'] = 'github'
        parsed_username = github_username.strip().split("/")[-1]
        with st.spinner(f"Hold on... Analyzing {parsed_username}'s GitHub portfolio... This may take a moment."):
            try:
                repos_data = get_user_repos(parsed_username, github_token)
                if not repos_data:
                    st.error(f"Could not find any valid repositories for user '{parsed_username}'. Please check the username and token.")
                    return

                skills, repo_skills = extract_skills(repos_data)
                
                # Score and sort repos for the showcase
                for repo in repos_data:
                    repo['score'] = (repo['star_count'] * 0.6) + (len(repo['readme_content']) * 0.2) + (len(repo_skills.get(repo['name'], [])) * 0.2)
                
                repos_data.sort(key=lambda x: x['score'], reverse=True)

                repos_data_clustered = cluster_projects(repos_data)
                scores = score_portfolio(repos_data_clustered, skills)
                recommendations = generate_recommendations(repos_data_clustered, skills)
                
                # Combine READMEs for a portfolio-level summary
                all_readme_content = " ".join(repo['readme_content'] for repo in repos_data if repo.get('readme_content'))
                summary = generate_summary(all_readme_content)

                st.session_state.update({
                    'analysis_complete': True, 'repos_data': repos_data_clustered,
                    'skills': skills, 'repo_skills': repo_skills, 
                    'scores': scores, 'recommendations': recommendations,
                    'summary': summary, 'username': parsed_username
                })

            except Exception as e:
                st.error(f"An unexpected error occurred during analysis: {e}")
                st.session_state['analysis_complete'] = False

    # --- LinkedIn Analysis Logic ---
    if linkedin_button and linkedin_file:
        st.session_state['analysis_type'] = 'linkedin'
        try:
            if linkedin_file.type == "application/pdf":
                linkedin_data = parse_linkedin_pdf(linkedin_file)
            else: # Assume HTML
                html_content = linkedin_file.getvalue().decode("utf-8")
                linkedin_data = parse_linkedin_profile(html_content)
            
            st.session_state['linkedin_data'] = linkedin_data
            st.session_state['analysis_complete'] = True
        except Exception as e:
            st.error(f"Could not parse the LinkedIn file: {e}")
            st.session_state['analysis_complete'] = False

    if st.session_state.get('analysis_complete'):
        if st.session_state.get('analysis_type') == 'github':
            display_github_results()
        elif st.session_state.get('analysis_type') == 'linkedin':
            display_linkedin_results()

def display_linkedin_results():
    """Renders the analysis results for a LinkedIn-only analysis."""
    st.header("LinkedIn Profile Analysis")
    linkedin_data = st.session_state['linkedin_data']

    if not any(linkedin_data.values()):
        st.error("Could not extract any information from the provided LinkedIn file. Please check the file and try again.")
        return

    # --- Generate and Display Recommendations ---
    st.subheader("💡 AI-Powered Profile Recommendations")
    with st.spinner("Analyzing your profile with local AI..."):
        recommendations = generate_linkedin_recommendations(linkedin_data)
    for rec in recommendations:
        st.info(rec)

    # --- Display Parsed Sections ---
    col1, col2 = st.columns(2)
    with col1:
        if linkedin_data.get("summary"):
            st.subheader("Professional Summary")
            st.text_area("", linkedin_data["summary"], height=200)
        
        if linkedin_data.get("skills"):
            st.subheader("Top Skills")
            st.markdown(", ".join(f"`{skill}`" for skill in linkedin_data["skills"]))

    with col2:
        if linkedin_data.get("experience"):
            st.subheader("Work Experience")
            for job in linkedin_data["experience"]:
                st.markdown(f"- **{job['title']}** at {job['company']}")
        
        if linkedin_data.get("education"):
            st.subheader("Education")
            for edu in linkedin_data["education"]:
                st.markdown(f"- **{edu['degree']}** from {edu['school']}")
        
        if linkedin_data.get("certifications"):
            st.subheader("Licenses & Certifications")
            for cert in linkedin_data["certifications"]:
                st.markdown(f"- **{cert['title']}** from {cert['issuer']}")

def display_github_results():
    """Renders the analysis results in tabs for GitHub analysis."""
    st.header(f"Analysis for {st.session_state['username']}")
    
    tab_titles = [
        "📊 Overview", "Deep Dive", "🛠️ Skill Map", 
        "🧩 Project Clusters", "🌱 Recommendations", "🎯 Career Planner"
    ]
    if st.session_state.get('linkedin_data'):
        tab_titles.insert(1, "🔗 LinkedIn Profile")

    tabs = st.tabs(tab_titles)
    tab_index = 0

    with tabs[tab_index]: # Overview
        # --- Create a Key Metrics Row ---
        repos_data = st.session_state['repos_data']
        total_repos = len(repos_data)
        
        most_starred_repo = max(repos_data, key=lambda x: x['star_count'])
        most_stars = most_starred_repo['star_count']
        most_starred_name = most_starred_repo['name']

        languages = [repo['primary_language'] for repo in repos_data if repo['primary_language'] != "Not specified"]
        primary_language = pd.Series(languages).mode()[0] if languages else "N/A"

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Repositories", total_repos)
        col2.metric("Most Stars", f"{most_stars} ⭐", f"on {most_starred_name}")
        col3.metric("Primary Language", primary_language)
        
        st.divider()

        # --- Showcase Projects ---
        st.subheader("🏆 Showcase Projects")
        top_3_repos = repos_data[:3]
        cols = st.columns(3)
        for i, repo in enumerate(top_3_repos):
            with cols[i]:
                with st.container(border=True):
                    st.markdown(f"**{repo['name']}**")
                    st.caption(repo['description'] if repo['description'] else "No description available.")
                    repo_skills = st.session_state['repo_skills'].get(repo['name'], [])
                    if repo_skills:
                        st.markdown("**Key Tech:** " + ", ".join(f"`{s}`" for s in list(repo_skills)[:3]))
                    st.markdown(f"⭐ {repo['star_count']} Stars")

        st.divider()

        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Overall Portfolio Score", f"{st.session_state['scores']['total_score']}/100")
            score_df = pd.DataFrame(dict(r=list(st.session_state['scores']['breakdown'].values()), theta=list(st.session_state['scores']['breakdown'].keys())))
            fig = px.line_polar(score_df, r='r', theta='theta', line_close=True, range_r=[0, 100], title="Score Breakdown")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("AI-Generated Summary")
            st.markdown(st.session_state['summary'])

        st.subheader("Contribution Heatmap")
        repos_data = st.session_state['repos_data']
        all_commits = []
        for repo in repos_data:
            all_commits.extend(repo['commits'])
        
        if all_commits:
            commit_dates = [commit.date() for commit in all_commits]
            commit_counts = pd.Series(commit_dates).value_counts().sort_index()
            
            # Create a full date range for the last year
            end_date = pd.to_datetime('today')
            start_date = end_date - pd.DateOffset(years=1)
            full_date_range = pd.date_range(start=start_date, end=end_date)
            
            # Reindex our commit counts to this full range
            commit_counts = commit_counts.reindex(full_date_range, fill_value=0)
            
            # Create the heatmap figure using Plotly
            fig = go.Figure(go.Heatmap(
                z=commit_counts.values,
                x=commit_counts.index,
                y=[''], # A single row for the heatmap
                colorscale='Greens',
                showscale=False,
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Commits: %{z}<extra></extra>'
            ))
            fig.update_layout(
                yaxis_nticks=0, 
                yaxis_visible=False,
                height=150,
                margin = dict(t=20, l=0, r=0, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No commit activity found in the last year.")
    tab_index += 1

    if st.session_state.get('linkedin_data'):
        with tabs[tab_index]: # LinkedIn Profile
            st.subheader("LinkedIn Profile Analysis")
            linkedin_data = st.session_state['linkedin_data']
            
            if linkedin_data.get("summary"):
                st.markdown("#### Professional Summary")
                st.info(linkedin_data["summary"])
            
            if linkedin_data.get("experience"):
                st.markdown("#### Work Experience")
                for job in linkedin_data["experience"]:
                    st.markdown(f"- **{job['title']}** at {job['company']}")
            
            if linkedin_data.get("skills"):
                st.markdown("#### Top Skills")
                st.markdown(", ".join(f"`{skill}`" for skill in linkedin_data["skills"][:10])) # Show top 10

        tab_index += 1

    with tabs[tab_index]: # Deep Dive
        st.subheader("Project Deep Dive")
        repos_df = pd.DataFrame(st.session_state['repos_data'])
        
        # Display a searchable, selectable table of projects
        selected_project_name = st.selectbox(
            "Select a project to see details:",
            options=repos_df['name'].tolist(),
            index=0
        )
        
        if selected_project_name:
            selected_repo = repos_df[repos_df['name'] == selected_project_name].iloc[0]
            
            st.write(f"### {selected_repo['name']}")
            st.write(selected_repo['description'])
            
            col1, col2 = st.columns(2)
            col1.metric("Stars", selected_repo['star_count'])
            col2.metric("Primary Language", selected_repo['primary_language'])
            
            with st.expander("View AI-Generated README Summary"):
                with st.spinner("Generating summary..."):
                    readme_summary = generate_readme_summary(selected_repo)
                    st.info(readme_summary)
    tab_index += 1

    with tabs[tab_index]: # Skill Map
        skills = st.session_state['skills']
        if skills:
            st.subheader("Skill Frequency")
            skill_df = pd.DataFrame(skills.items(), columns=['Skill', 'Projects']).sort_values('Projects', ascending=False)
            fig_bar = px.bar(skill_df, x='Projects', y='Skill', orientation='h', title='Technology Skills Detected')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No specific technical skills were detected from the predefined list.")
    tab_index += 1

    with tabs[tab_index]: # Project Clusters
        repos_data = st.session_state['repos_data']
        clustered_repos = [repo for repo in repos_data if 'cluster_id' in repo]
        
        if clustered_repos:
            df = pd.DataFrame(clustered_repos)
            
            # Create the scatter plot with new cluster names
            fig = px.scatter(
                df, x='x', y='y', 
                color='cluster_name',
                hover_name='name', 
                hover_data={'description': True}, 
                title='Project Clusters (UMAP)'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()

            # Display an interactive breakdown of each cluster
            st.subheader("Cluster Breakdown")
            for name in df['cluster_name'].unique():
                with st.expander(f"**Cluster: {name}**"):
                    cluster_df = df[df['cluster_name'] == name]
                    for _, repo in cluster_df.iterrows():
                        st.markdown(f"- **{repo['name']}**: {repo['description']}")

        else:
            st.info("Could not generate project clusters. This usually happens if project descriptions are missing.")
            
    with tabs[tab_index]: # Recommendations
        recommendations = st.session_state['recommendations']
        st.subheader("💡 New Project Ideas")
        st.markdown(recommendations.get('project_ideas', "No ideas generated."))
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔥 Recommended Skills to Learn")
            skills_to_learn = recommendations.get('skills_to_learn')
            if skills_to_learn:
                st.markdown("\n".join(f"- {skill}" for skill in skills_to_learn))
            else:
                st.success("Your skillset seems well-aligned with your projects!")
        with col2:
            st.subheader("🎓 Suggested Courses")
            courses = recommendations.get('suggested_courses')
            if courses:
                for skill, link in courses.items():
                    st.markdown(f"- **{skill}:** [Take a course]({link})")
            else:
                st.info("No specific course suggestions at this time.")
    tab_index += 1

    with tabs[tab_index]: # Career Planner
        st.subheader("Compare Your Skills to a Target Job Role")
        
        target_role = st.selectbox(
            "Select a target job role:",
            options=list(TARGET_JOB_SKILLS.keys())
        )
        
        if target_role:
            user_skills = set(st.session_state['skills'].keys())
            required_core = set(TARGET_JOB_SKILLS[target_role]["Core"])
            required_secondary = set(TARGET_JOB_SKILLS[target_role]["Secondary"])
            
            # Calculate match scores
            core_match = len(user_skills.intersection(required_core))
            total_core = len(required_core)
            match_percentage = int((core_match / total_core) * 100) if total_core > 0 else 0
            
            st.metric(f"Core Skill Match for {target_role}", f"{match_percentage}%", delta=f"{core_match} of {total_core} skills")
            
            # Create a comparison dataframe
            comparison_data = []
            for skill in required_core:
                comparison_data.append({"Skill": skill, "Type": "Core", "Status": "Have" if skill in user_skills else "Missing"})
            for skill in required_secondary:
                comparison_data.append({"Skill": skill, "Type": "Secondary", "Status": "Have" if skill in user_skills else "Missing"})
            
            if comparison_data:
                df_compare = pd.DataFrame(comparison_data)
                
                fig = px.bar(
                    df_compare,
                    x="Skill",
                    y="Type",
                    color="Status",
                    orientation='h',
                    title=f"Skill Gap Analysis for {target_role}",
                    color_discrete_map={"Have": "mediumseagreen", "Missing": "lightcoral"},
                    labels={"Type": ""}
                )
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    if 'analysis_complete' not in st.session_state:
        st.session_state['analysis_complete'] = False
    main() 