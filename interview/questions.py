# -*- coding: utf-8 -*-
"""Questions RH — chargées depuis data/hr_questions.csv."""

import csv
import json
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "hr_questions.csv"


def load_questions():
    """Charge les questions RH depuis le CSV."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {CSV_PATH}\n"
            f"Lance d'abord : python scripts\\build_hr_csv.py"
        )

    questions = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            q = {
                "id": row["id"],
                "question": row["question"],
                "ideal_answer": row["ideal_answer"],
                "keywords": row["keywords"].split("|") if row["keywords"] else [],
                "elements": json.loads(row["elements"]) if row["elements"] else {},
                "expected_duration": int(row["expected_duration"]),
                "weight": float(row["weight"]),
                "type": "standard",
            }
            questions.append(q)
    return questions


# Chargé à l'import
RH_QUESTIONS = load_questions()

# Compatibilité avec l'ancien nom utilisé par engine.py
STANDARD_RH_QUESTIONS = RH_QUESTIONS

# Fiches de poste
job_descriptions = {
    "Software Engineer": "Java, Python, OOP, Spring Boot, REST APIs, SQL, Git",
    "Data Scientist": "Python, ML, Deep Learning, Statistics, SQL, TensorFlow, PyTorch",
    "QA Analyst": "Testing, Selenium, Cypress, API testing, CI/CD, Bug tracking",
}


if __name__ == "__main__":
    print(f"✅ {len(RH_QUESTIONS)} questions chargées.")
    for q in RH_QUESTIONS:
        print(f"   [{q['id']}] {q['question']}")