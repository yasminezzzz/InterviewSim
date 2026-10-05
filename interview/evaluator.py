# -*- coding: utf-8 -*-
"""Évaluation des réponses : similarité + détection de concepts."""

from sentence_transformers import SentenceTransformer, util

# Le modèle est chargé UNE SEULE FOIS au premier import.
# (évite de le recharger à chaque appel)
_MODEL = None


def _get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL


def compute_similarity(text1, text2):
    """Similarité cosinus entre 2 textes (entre -1 et 1)."""
    model = _get_model()
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    return float(util.cos_sim(emb1, emb2)[0][0])


def detect_concepts(candidate, keywords):
    """Retourne (concepts trouvés, taux de couverture)."""
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]
    elif not isinstance(keywords, list):
        keywords = []
    candidate_lower = candidate.lower()
    found = [k for k in keywords if k.lower() in candidate_lower]
    coverage = len(found) / len(keywords) if keywords else 0
    return found, coverage


def get_quality_label(score):
    """Étiquette lisible pour un score."""
    if score >= 0.85:
        return "Excellente"
    elif score >= 0.70:
        return "Bonne"
    elif score >= 0.50:
        return "Moyenne"
    elif score >= 0.30:
        return "Insuffisante"
    else:
        return "Mauvaise"


def evaluate_answer(question, answer):
    """Évalue une réponse : similarité + mots-clés -> score global."""
    ideal = (
        question.get("ideal_answer")
        or question.get("expected_answer")
        or question.get("question", "")
    )
    if not isinstance(ideal, str) or len(ideal.strip()) < 5:
        ideal = str(question.get("question", "question"))
    if not isinstance(answer, str):
        answer = str(answer)

    sim = compute_similarity(ideal, answer)
    keywords = question.get("keywords", [])
    found, cov = detect_concepts(answer, keywords)
    score = (sim * 0.6) + (cov * 0.4)

    return {
        "similarity": round(sim, 3),
        "coverage": round(cov, 3),
        "concepts_found": found,
        "score": round(score, 3),
        "quality": get_quality_label(score),
    }


if __name__ == "__main__":
    # Test rapide
    q = {
        "ideal_answer": "I'm a software engineer with 3 years of experience in Java and Spring Boot.",
        "keywords": ["experience", "java", "backend"],
    }
    good = "I have 3 years of experience in backend development with Java."
    bad = "hey"
    print("Bonne réponse :", evaluate_answer(q, good))
    print("Mauvaise réponse :", evaluate_answer(q, bad))