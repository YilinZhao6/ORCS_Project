#!/usr/bin/env python3
import os
import json
from typing import List
from pydantic import BaseModel
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="MY_API_KEY")  # Use your API key from environment variable

# History file path
HISTORY_PATH = "source_files/conversation_history.json"
os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)

# ==== Structured Output Schema ====
class PrivacyStep(BaseModel):
    response: str
    continue_asking: bool

# ==== History Handling ====
def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)

# ==== Main Assistant Function ====
def run_privacy_decider():
    # Clear history before session
    save_history([])

    system_prompt = {
        "role": "system",
        "content" : "You are a Privacy Engineering Assistant tasked with advising organizations on the selection of appropriate privacy-preserving technologies (PETs) based on their specific use cases. Your primary objective is to systematically collect comprehensive and accurate contextual information regarding the user's data practices, regulatory obligations, risk tolerance, and intended data use. Refrain from making any recommendations until all relevant details have been gathered and verified. Depending on the intended audience, tailor the level of technicality accordingly (for instance, use less technical jargon when aimed towards business/legal audiences versus engineering teams).\n\n" \
        "You must ask questions **one at a time**, and base each next question on what has already been collected. Always wait for the user to respond before proceeding. Be brief, precise, and professional in your questioning.\n\n" \
        "Start by asking the user about their project — for example:\n" \
        "- What is the nature of the project? (e.g., health tech, finance, ML model training, social platform, etc.)\n" \
        "- What industry do you operate in, and what is the primary objective of your data processing activity?\n" \
        "- What types of data are involved? (e.g., personal data, sensitive health info, anonymized data, etc.)\n" \
        "- What types of data will you be processing, and how sensitive is this data on a scale of 1–5?\n" \
        "- Is your data structured, unstructured, or both, and approximately how many records/individuals are involved?\n" \
        "- What is the geographic scope? (e.g., Europe, U.S., global?)\n" \
        "- Which geographic regions and privacy regulations (e.g., GDPR, CCPA, HIPAA) apply to your use case?\n" \
        "- Is the data shared with external partners or kept internal?\n" \
        "- Will this data be shared externally, and if so, with whom?\n" \
        "- What kind of processing is performed on the data? (e.g., centralized, federated, encrypted compute?)\n" \
        "- Is your architecture centralized or decentralized, and where will processing occur (cloud, on-premises, or end-user devices?)\n" \
        "- Are real-time decisions made, or is this for batch analysis or training?\n" \
        "- How important is absolute accuracy in your results versus enhanced privacy protection?\n" \
        "- Do you need to perform joint computations with other organizations while keeping data private?\n" \
        "- Do you require formal mathematical privacy guarantees, or are industry best practices sufficient?\n" \
        "- What are your technical constraints regarding computational resources and performance requirements?\n" \
        "- Do you need to support data deletion or correction after processing (right to be forgotten)?\n" \
        "- What is your team's level of expertise with privacy technologies, and what is your implementation timeline?\n" \
        "- Who is the intended audience for these recommendations? (e.g., engineers, business, legal, etc.)\n\n" \
        "Ensure ALL of the questions are being asked. Once enough context is available to suggest appropriate PETs, set `continue_asking` to `false` and stop asking questions.\n\n" \
        "Do not make any recommendations yet — only collect and verify information."
    }

    messages = [system_prompt]
    history = []

    while True:
        user_input = input("🧑 You: ").strip()
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=messages,
                response_format=PrivacyStep
            )

            parsed: PrivacyStep = completion.choices[0].message.parsed
            print(f"🤖 ORCS AI: {parsed.response}")

            history.append({"user": user_input, "assistant": parsed.response})
            save_history(history)
            messages.append({"role": "assistant", "content": parsed.response})

            if not parsed.continue_asking:
                print("✅ Info collection complete. You can now make a recommendation based on this context.")
                break

        except Exception as e:
            print("❌ Error:", str(e))
            break

if __name__ == "__main__":
    run_privacy_decider()
