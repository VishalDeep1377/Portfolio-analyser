"""
This module uses a local Hugging Face transformer model to generate summaries.
It provides a free, offline alternative to paid LLM APIs.
"""
from transformers import pipeline
import torch
import streamlit as st

# Initialize the summarization pipeline using a small, efficient model.
# This will be cached, so the model is only loaded once.
@st.cache_resource
def get_summarizer():
    try:
        return pipeline(
            "summarization",
            model="t5-small",
            # Use a specific revision to ensure compatibility
            revision="d769bba", 
            # Forcing CPU usage if torch is available but CUDA is not configured
            device=-1 if not torch.cuda.is_available() else 0 
        )
    except Exception as e:
        print(f"Error initializing summarization pipeline: {e}")
        return None

def generate_summary(text_content):
    """
    Generates a summary for a given text using the local T5 model.

    Args:
        text_content (str): The text to be summarized (e.g., combined READMEs).

    Returns:
        str: The generated summary, or a fallback message if summarization fails.
    """
    summarizer = get_summarizer()
    if not summarizer:
        return "Summary generation is currently unavailable."
    
    # The model works best with text between 512 and 1024 tokens.
    # We truncate the text to ensure it fits within the model's context window.
    max_length = 1024
    if len(text_content) > max_length:
        text_content = text_content[:max_length]
        
    if not text_content.strip():
        return "Not enough content available to generate a summary."

    try:
        summary = summarizer(text_content, max_length=150, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"Error during summary generation: {e}")
        return "Could not generate a summary for the provided text."

def generate_readme_summary(repo):
    """
    Creates a summary specifically for a project's README.
    """
    if not repo['readme_content'] or not repo['readme_content'].strip():
        return "This project has no README content to summarize."
        
    prompt = f"Summarize the following README for the project '{repo['name']}':\n\n{repo['readme_content']}"
    return generate_summary(prompt) 