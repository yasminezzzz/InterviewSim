# -*- coding: utf-8 -*-
"""Évaluation des réponses : classifieur ML (si dispo) + fallback similarité.

- `compute_similarity` : similarité cosinus entre 2 textes (via le modèle)
- `detect_concepts` : détection SÉMANTIQUE des concepts attendus
- `evaluate_answer` : score calibré + qualité prédite par le classifieur
"""

from pathlib import Path
import joblib
from sentence_transformers import SentenceTransformer, util

# Chemins vers les modèles
_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "interview-encoder-v7"
_CLASSIFIER_PATH = Path(__file__).resolve().parents[1] / "models" / "classifier_rf.pkl"

# Chargés UNE SEULE FOIS
_MODEL = None
_CLASSIFIER = None

# Seuil pour la détection sémantique des concepts
CONCEPT_THRESHOLD = 0.4

# Calibration : retire le bruit de fond du modèle
BASE = 0.30


def _get_model():
    """Charge le modèle fine-tuné (une seule fois)."""
    global _MODEL
    if _MODEL is None:
        if not _MODEL_PATH.exists():
            raise FileNotFoundError(f"Modèle introuvable : {_MODEL_PATH}")
        _MODEL = SentenceTransformer(str(_MODEL_PATH))
    return _MODEL


def _get_classifier():
    """Charge le classifieur RandomForest (une seule fois). Retourne None s'il n'existe pas."""
    global _CLASSIFIER
    if _CLASSIFIER is None:
        if _CLASSIFIER_PATH.exists():
            _CLASSIFIER = joblib.load(_CLASSIFIER_PATH)
        else:
            _CLASSIFIER = False   # marqueur "absent"
    return _CLASSIFIER if _CLASSIFIER else None


def compute_similarity(text1, text2):
    """Similarité cosinus entre 2 textes (entre -1 et 1)."""
    model = _get_model()
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    return float(util.cos_sim(emb1, emb2)[0][0])


def detect_concepts(candidate, keywords):
    """Détection SÉMANTIQUE des concepts (par le sens, pas par mots exacts)."""
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]
    elif not isinstance(keywords, list):
        keywords = []

    if not keywords:
        return [], 0.0

    model = _get_model()
    emb_candidate = model.encode(candidate, convert_to_tensor=True)

    found = []
    for kw in keywords:
        emb_kw = model.encode(kw, convert_to_tensor=True)
        sim = float(util.cos_sim(emb_candidate, emb_kw)[0][0])
        if sim >= CONCEPT_THRESHOLD:
            found.append(kw)

    coverage = len(found) / len(keywords)
    return found, coverage


def get_quality_label(score):
    """Étiquette par seuils (fallback si pas de classifieur)."""
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
    """Évaluation d'une réponse.

    1. Calcule la similarité avec la réponse idéale (via le modèle fine-tuné).
    2. Applique la calibration pour retirer le bruit de fond.
    3. Extrait 5 features.
    4. Utilise le classifieur RandomForest (s'il existe) pour prédire la qualité.
    5. Sinon, fallback sur les seuils.
    """
    ideal = (
        question.get("ideal_answer")
        or question.get("expected_answer")
        or question.get("question", "")
    )
    if not isinstance(ideal, str) or len(ideal.strip()) < 5:
        ideal = str(question.get("question", "question"))
    if not isinstance(answer, str):
        answer = str(answer)

    # 1. Similarité brute
    sim = compute_similarity(ideal, answer)

    # 2. Calibration
    score = max(0.0, (sim - BASE) / (1.0 - BASE))

    # 3. Concepts détectés
    keywords = question.get("keywords", [])
    found, cov = detect_concepts(answer, keywords)

    # 4. Extraction des 5 features
    len_ideal = max(1, len(ideal.split()))
    len_answer = max(1, len(answer.split()))
    length_ratio = min(2.0, len_answer / len_ideal)

    features = [
        sim,                     # 1. similarité brute
        len(answer.split()),     # 2. nombre de mots
        cov,                     # 3. couverture des concepts
        len(found),              # 4. nombre de concepts trouvés
        length_ratio,            # 5. ratio longueur réponse/idéal
    ]

    # 5. Prédiction via le classifieur (si dispo)
    clf = _get_classifier()
    if clf is not None:
        try:
            label = clf.predict([features])[0]
        except Exception:
            label = get_quality_label(score)
    else:
        label = get_quality_label(score)

    return {
        "similarity": round(sim, 3),
        "coverage": round(cov, 3),
        "concepts_found": found,
        "score": round(score, 3),
        "quality": label,
        "features": {
            "similarity": round(sim, 3),
            "num_words": len(answer.split()),
            "coverage": round(cov, 3),
            "num_concepts": len(found),
            "length_ratio": round(length_ratio, 3),
        },
    }


if __name__ == "__main__":
    print("🧪 Test de l'évaluateur (avec classifieur ML)\n")
    print(f"Modèle      : {_MODEL_PATH}")
    print(f"Classifieur : {_CLASSIFIER_PATH}")
    print(f"Classifieur présent : {_CLASSIFIER_PATH.exists()}\n")

    q = {
        "ideal_answer": "Hi, I'm Alex. I'm a software engineer with 5 years of experience specializing in backend development with Java, Spring Boot, and PostgreSQL. I led a team of 3 developers on a microservices migration that reduced latency by 40 percent.",
        "keywords": ["experience", "java", "backend"],
    }

    tests = [
        ("Hey", "mauvaise"),
        ("nothing", "mauvaise"),
        ("Everything is very recognises.", "mauvaise"),
        ("I am a developer.", "insuffisante"),
        ("I have 3 years of experience in Java.", "moyenne"),
        ("I'm a software engineer with 3 years of experience in Java and Spring Boot.", "bonne"),
        ("Hi, I'm Alex. I'm a software engineer with 5 years of experience specializing in backend development with Java, Spring Boot, and PostgreSQL. I led a team of 3 developers on a microservices migration that reduced latency by 40 percent.", "excellente"),
    ]

    for answer, expected in tests:
        result = evaluate_answer(q, answer)
        print(f"Réponse ({expected:12s}) : {answer[:60]}")
        print(f"  → sim = {result['similarity']:.3f} | score = {result['score']} | qualité = {result['quality']}")
        print()