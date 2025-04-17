import os
import numpy as np
from openai import OpenAI
import tiktoken
from tqdm import tqdm
import time

# Initialize OpenAI client
client = OpenAI(api_key="PUT API KEY HERE")  # Use your API key from environment variable

def get_embeddings(text_chunks, model="text-embedding-3-large"):
    """
    Get embeddings for a list of text chunks using OpenAI's embedding model.
    
    Args:
        text_chunks (list): List of text strings to embed
        model (str): OpenAI embedding model to use
        
    Returns:
        list: List of embedding vectors
    """
    embeddings = []
    
    # Process in batches to handle potential API limits
    batch_size = 100  # Adjust based on your needs and API limits
    
    # Create progress bar
    total_batches = (len(text_chunks) + batch_size - 1) // batch_size
    start_time = time.time()
    
    with tqdm(total=len(text_chunks), desc="Generating embeddings") as pbar:
        for i in range(0, len(text_chunks), batch_size):
            batch = text_chunks[i:i + batch_size]
            
            response = client.embeddings.create(
                input=batch,
                model=model
            )
            
            # Extract embedding data from response
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
            
            # Update progress bar
            pbar.update(len(batch))
            
            # Calculate and display estimated time remaining
            elapsed = time.time() - start_time
            done = len(embeddings)
            total = len(text_chunks)
            if done > 0:
                rate = elapsed / done
                eta = rate * (total - done)
                pbar.set_postfix({"ETA": f"{eta:.2f}s"})
    
    return embeddings

def chunk_text(text, chunk_size=1000, overlap=100):
    """
    Split text into chunks of specified size with optional overlap.
    
    Args:
        text (str): Input text to chunk
        chunk_size (int): Maximum number of tokens per chunk
        overlap (int): Number of overlapping tokens between chunks
        
    Returns:
        list: List of text chunks
    """
    # Get tokenizer for text-embedding-3 models (using cl100k_base encoding)
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    
    chunks = []
    i = 0
    
    while i < len(tokens):
        # Get chunk of tokens
        chunk_end = min(i + chunk_size, len(tokens))
        chunk = tokens[i:chunk_end]
        
        # Decode tokens back to text
        chunk_text = encoding.decode(chunk)
        chunks.append(chunk_text)
        
        # Move to next chunk with overlap
        i += chunk_size - overlap
    
    return chunks

def main():
    # Create vectors directory if it doesn't exist
    os.makedirs("vectors", exist_ok=True)
    
    # Read source file
    with open("source_files/source.txt", "r", encoding="utf-8") as f:
        text = f.read()
    
    # Split into chunks
    chunks = chunk_text(text)
    print(f"Split text into {len(chunks)} chunks")
    
    # Get embeddings
    embeddings = get_embeddings(chunks)
    
    # Save text chunks and embeddings to vectors folder
    np.save("vectors/text.npy", np.array(chunks, dtype=object))
    np.save("vectors/embeddings.npy", np.array(embeddings))
    
    print(f"Saved {len(chunks)} chunks and embeddings to vectors/text.npy and vectors/embeddings.npy")
    print(f"Embedding dimensions: {len(embeddings[0])}")

if __name__ == "__main__":
    main()