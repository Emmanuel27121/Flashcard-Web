import csv
import json
import os


from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing. Add it to backend/.env.")

client = OpenAI(api_key=api_key)
# client = OpenAI(api_key="put your key here")  # Replace with your actual API key or use environment variable

def generate_flashcards(text:str) -> list[dict[str, str]]:

    promt = f"""
Create up to 10 useful study flashcards from the material below.

Rules:
- Each flashcard needs a short, clear question and answer.
- Focus on the most important concepts.
- Do not invent information not found in the text.
- Return JSON only, using this exact shape:

{{
  "flashcards": [
    {{
      "question": "Question here",
      "answer": "Answer here"
    }}
  ]
}}

Study material:
{text}
"""
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You generate helpful study flashcards."},
            {"role": "user", "content": promt}
        ]
    )
    
    content = response.choices[0].message.content

    if not content:
        raise ValueError("The AI returned an empty response.")
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError("The AI returned invalid JSON.") from e

    cards = data.get("flashcards")

    if not isinstance(cards, list):
        raise ValueError("The AI returned an unexpected format for flashcards.")

    valid_cards = []

    for card in cards:
        if not isinstance(card, dict):
            continue

        question = card.get("question")
        answer = card.get("answer")

        if isinstance(question, str) and isinstance(answer, str):
            question = question.strip()
            answer = answer.strip()

            if question and answer:
                valid_cards.append({"question": question, "answer": answer})

    return valid_cards


def generate_flashcards_from_chunks(chunks: list[str]) -> list[dict[str, str]]:
    all_cards = []

    for chunk in chunks:
        all_cards.extend(generate_flashcards(chunk))

    return all_cards



def save_flashcards(cards: list[dict[str, str]], filename: str) -> None:
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Question", "Answer"])

        for card in cards:
            writer.writerow([card["question"], card["answer"]])