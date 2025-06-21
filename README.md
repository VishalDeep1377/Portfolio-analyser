# 🚀 Professional AI-Powered Portfolio Analyzer

This Streamlit web application provides a comprehensive analysis of a data scientist's or software engineer's professional presence by parsing both GitHub repositories and LinkedIn profiles. It uses local, open-source AI models to generate insights, ensuring all analysis is performed privately and for free.

This tool is designed to help users identify their strengths, discover skill gaps, and find actionable steps to improve their professional portfolio.

## ✨ Features

- **Dual Profile Analysis**: Analyze a GitHub profile, a LinkedIn profile, or both.
- **In-Depth GitHub Analysis**:
    - Fetches all public, non-forked repositories.
    - Extracts key skills and technologies from code and documentation.
    - Calculates a portfolio score based on diversity, popularity, and documentation quality.
    - Visualizes project clusters to identify core domain areas (e.g., NLP, Web Dev).
    - Renders a GitHub-style contribution heatmap to showcase consistency.
- **Intelligent LinkedIn Parsing**:
    - Parses user-uploaded HTML or PDF profiles safely and locally.
    - Extracts summary, work experience, education, skills, and certifications.
    - **AI-Powered Recommendations**: Uses a local AI model (`t5-small`) to provide contextual, actionable advice on improving profile text.
- **Career Planner**:
    - Compares a user's skillset against ideal profiles for roles like Data Analyst, Data Scientist, and MLOps Engineer.
    - Provides a "Match Score" and visual skill-gap analysis.
- **Interactive Dashboard**:
    - Built with Streamlit for a clean, professional, and interactive user experience.
    - Features key metrics, interactive charts, and a project deep-dive section.
- **100% Free and Local**: All analysis and AI-powered features run locally. No API keys or paid services are required to run the core application.

## 🛠️ Tech Stack

- **Backend**: Python
- **Frontend**: Streamlit
- **Data Analysis**: Pandas, NumPy, Scikit-learn
- **Local AI**: Hugging Face `transformers`, `sentence-transformers`, `torch`
- **Visualizations**: Plotly
- **File Parsing**: PyGithub, BeautifulSoup, pdfplumber

## ⚙️ Setup and Installation

Follow these steps to run the application locally.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd portfolio-analyzer
```

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install all the required packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```
The first time you run the app, it may need to download the open-source models (approx. 300-500 MB). This is a one-time process.

## 🚀 How to Run the App

Once the setup is complete, you can launch the Streamlit application with a single command:

```bash
streamlit run portfolio_analyzer/app.py
```

Your web browser will automatically open with the application running.

## 📋 How to Use the App

1.  **For GitHub Analysis**:
    -   Generate a GitHub Personal Access Token with `public_repo` scope. The app includes a guide on how to do this.
    -   Enter your GitHub username and the token into the sidebar.
    -   Click "Analyze GitHub Portfolio".

2.  **For LinkedIn Analysis**:
    -   Download your LinkedIn profile as a PDF or save the page as an HTML file. The app includes a guide for this.
    -   Upload the file using the file uploader in the sidebar.
    -   Click "Analyze LinkedIn Profile". 