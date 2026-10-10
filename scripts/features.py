# -*- coding: utf-8 -*-
"""Extraction de features pour le classifieur ML."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from interview.evaluator import compute_similarity, detect_concepts

FEATURE_NAMES = ["similarity", "num_words", "coverage", "num_concepts", "length_ratio"]


def extract_features(ideal_answer, candidate_answer, keywords=None):
    """Retourne un dict de features."""
    if keywords is None:
        keywords = []

    similarity = compute_similarity(ideal_answer, candidate_answer)
    num_words = len(candidate_answer.split())
    found, coverage = detect_concepts(candidate_answer, keywords)
    num_concepts = len(found)

    len_ideal = max(1, len(ideal_answer.split()))
    len_candidate = max(1, len(candidate_answer.split()))
    length_ratio = min(2.0, len_candidate / len_ideal)

    return {
        "similarity": similarity,
        "num_words": num_words,
        "coverage": coverage,
        "num_concepts": num_concepts,
        "length_ratio": length_ratio,
    }


def features_to_vector(features):
    """Convertit le dict de features en liste ordonnée."""
    return [features[name] for name in FEATURE_NAMES]


if __name__ == "__main__":
    print("✅ features.py OK")
    ideal = "Hi, I'm Alex. I'm a software engineer with 5 years of experience."
    keywords = ["experience", "engineer"]

    print("Mauvaise :", features_to_vector(extract_features(ideal, "hey", keywords)))
    print("Bonne    :", features_to_vector(extract_features(ideal, "I have 5 years of experience as a software engineer.", keywords)))