import os
import json
from typing import List
from pydantic import BaseModel
from openai import OpenAI
from vector_search import search_vectors

# === Setup ===
client = OpenAI(api_key="PUT API KEY HERE")  # Use your API key from environment variable
HISTORY_PATH = "source_files/conversation_history.json"

# === Step 1: Define Pydantic schema ===
class ProjectSummary(BaseModel):
    summary: str

# === Step 2: Load conversation history ===
def load_conversation():
    if not os.path.exists(HISTORY_PATH):
        raise FileNotFoundError("Conversation history not found.")
    with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
        return f.read()  # Just return the raw JSON content as a string


# === Step 3: Summarize the project context ===
def summarize_project(convo: str) -> str:
    system_prompt = {
        "role": "system",
        "content": "You are an assistant that summarizes a user's project based on their answers. Generate a one-sentence summary that captures their use case, data types, compliance concerns, geography, and technical goals."
    }
    user_prompt = {
        "role": "user",
        "content": f"Here is the conversation history:\n{convo}\n\nNow summarize the project in one sentence."
    }
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[system_prompt, user_prompt],
        response_format=ProjectSummary
    )
    return response.choices[0].message.parsed.summary

# === Step 4: Vector search ===
def retrieve_chunks(summary: str, top_k: int = 10) -> List[str]:
    results = search_vectors(query=summary, top_k=top_k)
    chunks = [chunk for chunk, _ in results]

    # save to file
    os.makedirs("source_files", exist_ok=True)
    with open("source_files/vector_search_results.txt", "w", encoding="utf-8") as f:
        for i, (chunk, score) in enumerate(results):
            f.write(f"[{i+1}] Similarity: {score:.4f} ({score*100:.2f}%)\n")
            f.write("-" * 80 + "\n")
            f.write(chunk.strip() + "\n")
            f.write("-" * 80 + "\n\n")
    
    return chunks


# === Step 5: Generate PET recommendations ===
def generate_recommendation(convo: str, summary: str, context_chunks: List[str]) -> str:
    context = "\n\n".join(context_chunks)
    prompt = f"""
You are a Privacy-Preserving Technology Advisor. Using the user's project description, conversation history, and relevant internal documentation, recommend the most suitable Privacy-Enhancing Technologies (PETs) for their specific use case.

Adapt the level of technical detail to the intended audience:
- For technical stakeholders (e.g., engineers, data scientists), provide highly detailed implementation guidance (what tools are necessary, and the key steps), technical specifications, and key configuration options.
- For non-technical stakeholders, offer thorough explanations of the relevant concepts, practical implications, and strategic considerations in clear, accessible language.

Focus on:
- Prioritizing recommendations based on the user's stated goals, constraints, and risk tolerance.
- Analyzing and clearly articulating the trade-offs, limitations, and dependencies associated with each recommendation.

Conversation Summary:
{summary}

Conversation History:
{convo}

Relevant Internal Documentation:
{context}

Your response must be structured and include:
- A prioritized list of recommended PETs
- Justifications for each recommendation
- Potential limitations, risks, or trade-offs
- (Optional) Suggested combinations of technologies, if beneficial

Use clear headings and bullet points to organize your response for readability.
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# === Main logic ===
def main():
    print("🔍 Loading conversation history...")
    convo = load_conversation()

    print("🧠 Summarizing project context...")
    summary = summarize_project(convo)
    print("✅ Summary:", summary)

    print("📚 Retrieving relevant documents...")
    chunks = retrieve_chunks(summary)

    print("🤖 Generating recommendations...")
    recommendations = generate_recommendation(convo, summary, chunks)

    print("\n📌 Final Recommendation:\n")
    print(recommendations)

    # save to markdown file
    with open("source_files/recommendations.md", "w", encoding="utf-8") as f:
        f.write(recommendations)

if __name__ == "__main__":
    main()
