#!/usr/bin/env python3
import os
import json
from typing import List
from pydantic import BaseModel
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="PUT API KEY HERE")  # Use your API key from environment variable

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
        "content": "You are a privacy engineering assistant designed to help organizations decide which privacy-preserving technologies (PETs) are appropriate for their specific use-case. Your goal is to collect complete context about the user's application before recommending any PETs. \
You must ask questions **one at a time**, and base each next question on what has already been collected. \
Start by asking the user about their project — for example:\n\
- What is the nature of the project? (e.g., health tech, finance, ML model training, social platform, etc.)\n\
- What types of data are involved? (e.g., personal data, sensitive health info, anonymized data, etc.)\n\
- What is the geographic scope? (e.g., Europe, U.S., global?)\n\
- Is the data shared with external partners or kept internal?\n\
- Is the organization under compliance obligations (e.g., GDPR, HIPAA)?\n\
- What kind of processing is performed on the data? (e.g., centralized, federated, encrypted compute?)\n\
- Are real-time decisions made, or is this for batch analysis or training?\n\
Ask questions **one at a time**, and be brief and precise. Wait for the user to respond before proceeding. \
Once you have enough information to suggest a suitable PET approach, set `continue_asking` to false and stop asking questions. \
Do not make recommendations. Only collect information."
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
                model="gpt-4o-mini",
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
