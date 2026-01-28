import csv
import re

def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def _title_case_term(term: str) -> str:
    term = term.strip(" .:-")
    return term[0].upper() + term[1:] if term else term


def generate_flashcard(chunks):
    cards = []
    i = 0

    while i < len(chunks):
        chunk = _clean(chunks[i])


        patterns = [
            (r"^(.+?)\s+is\s+(.+)$", "What is {term}?", "{defn}"),
            (r"^(.+?)\s+refers to\s+(.+)$", "What does {term} refer to?", "{defn}"),
            (r"^(.+?)\s+means\s+(.+)$", "What does {term} mean?", "{defn}"),
            (r"^(.+?)\s+is defined as\s+(.+)$", "Define {term}.", "{defn}"),
            (r"^(.+?)\s+occurs when\s+(.+)$", "When does {term} occur?", "{defn}"),
            (r"^(.+?)\s+is called\s+(.+)$", "What is {term} called?", "{defn}")
        ]

        made_card = False

        for pat, qfmt, afmt in patterns:
            m = re.match(pat, chunk, flags = re.IGNORECASE)
            if m:
                term = _title_case_term(m.group(1))
                defn = _clean(m.group(2)).rstrip(" .")
                q = qfmt.format(term=term)
                a = afmt.format(defn=defn)
                cards.append((q, a))
                made_card = True
                break

        if made_card:
            i += 1
            continue


        m = re.search(r"(.+?)\s+because\s+(.+)", chunk, flags = re.IGNORECASE)
        if m:
            effect = _clean(m.group(1)).rstrip(".")
            cause = _clean(m.group(2)).rstrip(".")
            cards.append((f"Why {effect.lower()}?",cause))
            i += 1
            continue


        if ";" in chunk and " but " in chunk.lower():
            parts = [p.strip() for p in chunk.split(";") if p.strip()]

            if len(parts) >= 2:
                cards.append(("Compare the following trade-offs:", " | ".join(parts)))
                i += 1
                continue

        i += 1


    depub = []
    seen = set()
    for q, a in cards:
        key = (q.lower().strip(), a.lower().strip())
        if  key not in seen:
            seen.add(key)
            depub.append((q, a))

    return depub

def save_flashcard(cards, path):
    with open(path, "w", newline = "", encoding = "utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Question", "Answer"])
        for question, answer in cards:
            writer.writerow([question, answer])