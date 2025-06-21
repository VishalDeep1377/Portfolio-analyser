# portfolio_analyzer/cluster_projects.py

"""
This module clusters projects into different domains using sentence embeddings (BERT)
and KMeans clustering. It includes a method to find the optimal number of clusters.
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import umap.umap_ as umap
import json
from collections import Counter
import streamlit as st
from sklearn.metrics import silhouette_score

# Load the sentence transformer model once
@st.cache_resource
def get_sentence_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def get_optimal_k(embeddings, max_k=10):
    """
    Finds the optimal number of clusters (k) using the Elbow Method.

    Args:
        embeddings (np.array): A numpy array of project embeddings.
        max_k (int): The maximum number of clusters to test.

    Returns:
        int: The optimal number of clusters (k).
    """
    if len(embeddings) < 2:
        return 1
        
    # Ensure max_k is not greater than the number of samples
    max_k = min(max_k, len(embeddings) - 1)
    if max_k < 2:
        return 1

    inertias = []
    k_range = range(1, max_k + 1)

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        kmeans.fit(embeddings)
        inertias.append(kmeans.inertia_)
    
    # Heuristic to find the "elbow" in the inertia plot.
    # We look for the point with the largest drop in inertia.
    if len(inertias) < 2:
        return 1

    deltas = [inertias[i] - inertias[i+1] for i in range(len(inertias)-1)]
    if not deltas:
        return 1
        
    # The optimal k is the one after the largest drop.
    optimal_k = deltas.index(max(deltas)) + 2 

    return optimal_k

def _get_top_keywords(text_list, top_n=2):
    """A simple helper to find common keywords, excluding very common words."""
    words = " ".join(text_list).lower().split()
    # Basic stopword list
    stopwords = {'the', 'a', 'an', 'in', 'to', 'for', 'of', 'and', 'is', 'with', 'on', 'using', 'by'}
    words = [word for word in words if word.isalnum() and word not in stopwords]
    most_common = Counter(words).most_common(top_n)
    return [word for word, freq in most_common]

@st.cache_data
def cluster_projects(repos_data):
    """
    Clusters projects based on their descriptions using sentence embeddings and KMeans.

    Args:
        repos_data (list): A list of repository dictionaries.

    Returns:
        list: The same list, with 'cluster', 'x', and 'y' keys added to each repo dict.
              'x' and 'y' are for 2D visualization with UMAP.
              Returns the original list if clustering cannot be performed.
    """
    # Filter out repos with no description, as they cannot be clustered.
    valid_repos = [repo for repo in repos_data if repo.get("description", "").strip()]

    if not valid_repos:
        print("No repositories with descriptions found to cluster.")
        return repos_data

    descriptions = [repo["description"] for repo in valid_repos]
    
    # Use a cached model to avoid reloading
    model = get_sentence_model()
    embeddings = model.encode(descriptions, show_progress_bar=False)

    # Find the optimal number of clusters
    num_repos = len(valid_repos)
    # Cap max_k to a reasonable number, e.g., 1/3 of repos, but at most 10.
    max_k = min(10, max(1, num_repos // 3))
    optimal_k = get_optimal_k(embeddings, max_k=max_k)

    # Perform clustering
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init='auto')
    kmeans.fit(embeddings)

    # Reduce dimensionality for visualization using UMAP
    # Ensure n_neighbors is less than the number of samples
    n_neighbors = min(15, len(embeddings) - 1)
    if n_neighbors < 2: # UMAP requires at least 2 neighbors
        print("Not enough data points for UMAP visualization.")
        umap_embeddings = np.zeros((len(embeddings), 2))
    else:
        umap_reducer = umap.UMAP(n_neighbors=n_neighbors, n_components=2, random_state=42)
        umap_embeddings = umap_reducer.fit_transform(embeddings)

    # Add the cluster labels back to the original repo data
    repo_data_map = {repo["name"]: repo for repo in repos_data}

    # --- Name the clusters based on content ---
    cluster_content = {i: [] for i in range(optimal_k)}
    for i, repo in enumerate(valid_repos):
        cluster_id = kmeans.labels_[i]
        cluster_content[cluster_id].append(repo["name"] + " " + repo["description"])

    cluster_names = {}
    for cluster_id, content in cluster_content.items():
        if content:
            keywords = _get_top_keywords(content)
            cluster_names[cluster_id] = " / ".join(keywords).capitalize()
        else:
            cluster_names[cluster_id] = f"Cluster {cluster_id}"

    for i, repo in enumerate(valid_repos):
        cluster_id = kmeans.labels_[i]
        repo_data_map[repo["name"]]["cluster_id"] = cluster_id
        repo_data_map[repo["name"]]["cluster_name"] = cluster_names[cluster_id]
        repo_data_map[repo["name"]]["x"] = umap_embeddings[i, 0]
        repo_data_map[repo["name"]]["y"] = umap_embeddings[i, 1]

    return list(repo_data_map.values()) 