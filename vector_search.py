#usage: python vector_search.py "differential privacy" --top 5

import os
import sys
import numpy as np
from openai import OpenAI
import argparse
from sklearn.metrics.pairwise import cosine_similarity

# Initialize OpenAI client
client = OpenAI(api_key="PUT API KEY HERE")  # Use your API key from environment variable

def load_vectors(vectors_dir="vectors"):
    """
    Load the previously saved text chunks and their embeddings.
    
    Args:
        vectors_dir (str): Directory containing the vector files
        
    Returns:
        tuple: (text_chunks, embeddings)
    """
    text_path = os.path.join(vectors_dir, "text.npy")
    embeddings_path = os.path.join(vectors_dir, "embeddings.npy")
    
    if not os.path.exists(text_path) or not os.path.exists(embeddings_path):
        print(f"Error: Vector files not found in {vectors_dir}")
        print(f"Make sure that {text_path} and {embeddings_path} exist")
        sys.exit(1)
    
    try:
        text_chunks = np.load(text_path, allow_pickle=True)
        embeddings = np.load(embeddings_path, allow_pickle=True)
        return text_chunks, embeddings
    except Exception as e:
        print(f"Error loading vector files: {e}")
        sys.exit(1)

def get_query_embedding(query, model="text-embedding-3-large"):
    """
    Get embedding for a search query using OpenAI's embedding model.
    
    Args:
        query (str): Search query text
        model (str): OpenAI embedding model to use
        
    Returns:
        list: Embedding vector for the query
    """
    try:
        response = client.embeddings.create(
            input=[query],
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting query embedding: {e}")
        sys.exit(1)

def search_vectors(query, top_k=10, vectors_dir="vectors"):
    """
    Search for the most similar text chunks to the query.
    
    Args:
        query (str): Search query text
        top_k (int): Number of top results to return
        vectors_dir (str): Directory containing the vector files
        
    Returns:
        list: List of (chunk, similarity_score) tuples
    """
    # Load text chunks and embeddings
    text_chunks, embeddings = load_vectors(vectors_dir)
    
    # Get embedding for the query
    query_embedding = get_query_embedding(query)
    
    # Calculate cosine similarity between query and all chunks
    query_embedding_array = np.array(query_embedding).reshape(1, -1)
    embeddings_array = np.array(embeddings.tolist())
    
    similarities = cosine_similarity(query_embedding_array, embeddings_array)[0]
    
    # Get indices of top_k most similar chunks
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    # Return top_k chunks with their similarity scores
    results = []
    for idx in top_indices:
        results.append((text_chunks[idx], similarities[idx]))
    
    return results

def format_results(results):
    """
    Format search results for display.
    
    Args:
        results (list): List of (chunk, similarity_score) tuples
        
    Returns:
        str: Formatted results string
    """
    output = []
    output.append("\n" + "="*80)
    output.append("SEARCH RESULTS")
    output.append("="*80)
    
    for i, (chunk, score) in enumerate(results, 1):
        # Truncate chunk if it's too long for display
        display_chunk = chunk
        if len(display_chunk) > 300:
            display_chunk = display_chunk[:300] + "..."
        
        # Format each result
        output.append(f"\n[{i}] Similarity: {score:.4f} ({score*100:.2f}%)")
        output.append("-"*80)
        output.append(display_chunk)
        output.append("-"*80)
    
    return "\n".join(output)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Vector search on embedded text chunks")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--top", type=int, default=10, help="Number of top results to return")
    parser.add_argument("--dir", type=str, default="vectors", help="Directory containing vector files")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Search vectors
    results = search_vectors(args.query, args.top, args.dir)
    
    # Display results
    print(format_results(results))

if __name__ == "__main__":
    main()