

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import joblib
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics import accuracy_score

# Seuils pour la méthode 1 et 2
SCORE_TO_LABEL = [
    (0.85, "Excellente"),
    (0.60, "Bonne"),
    (0.40, "Moyenne"),
    (0.20, "Insuffisante"),
    (0.0, "Mauvaise"),
]

BASE = 0.20
TEST_FILE = ROOT / "data" / "test.csv"
FINETUNED_PATH = str(ROOT / "models" / "interview-encoder-v7")
CLASSIFIER_PATH = ROOT / "models" / "classifier_rf.pkl"


def score_to_label(score):
    for threshold, label in SCORE_TO_LABEL:
        if score >= threshold:
            return label
    return "Mauvaise"


def evaluate_similarity_only(model_name_or_path, df, display_name):
    """Méthode 1 & 2 : similarité + seuils."""
    print(f"   🧠 Chargement du modèle : {display_name}")
    model = SentenceTransformer(model_name_or_path)
    y_true, y_pred = [], []
    for _, row in df.iterrows():
        emb_ideal = model.encode(row["ideal_answer"], convert_to_tensor=True)
        emb_cand = model.encode(row["candidate_answer"], convert_to_tensor=True)
        sim = float(util.cos_sim(emb_ideal, emb_cand)[0][0])
        score = max(0.0, (sim - BASE) / (1.0 - BASE))
        y_true.append(row["label"])
        y_pred.append(score_to_label(score))
    return accuracy_score(y_true, y_pred)


def evaluate_with_classifier(df):
    """Méthode 3 : similarité + classifieur RandomForest."""
    print("   🧠 Chargement du modèle fine-tuné + classifieur")
    model = SentenceTransformer(FINETUNED_PATH)
    clf = joblib.load(CLASSIFIER_PATH)

    y_true, y_pred = [], []
    for _, row in df.iterrows():
        emb_ideal = model.encode(row["ideal_answer"], convert_to_tensor=True)
        emb_cand = model.encode(row["candidate_answer"], convert_to_tensor=True)
        sim = float(util.cos_sim(emb_ideal, emb_cand)[0][0])

        # Mêmes features que dans train_classifier.py
        num_words = len(row["candidate_answer"].split())
        len_ideal = max(1, len(row["ideal_answer"].split()))
        len_cand = max(1, len(row["candidate_answer"].split()))
        length_ratio = min(2.0, len_cand / len_ideal)

        features = [sim, num_words, 0.0, 0, length_ratio]
        label = clf.predict([features])[0]

        y_true.append(row["label"])
        y_pred.append(label)
    return accuracy_score(y_true, y_pred)


def main():
    print("=" * 70)
    print("   COMPARAISON DES 2 MÉTHODES")
    print("=" * 70)

    df = pd.read_csv(TEST_FILE)
    print(f"\n📂 Test set : {len(df)} lignes\n")

    print("🌲 Méthode 1 : Modèle ORIGINAL (all-MiniLM-L6-v2) + seuils")
    acc1 = evaluate_similarity_only("all-MiniLM-L6-v2", df, "all-MiniLM-L6-v2")
    print(f"   → Accuracy : {acc1:.3f}\n")



    print("🌲 Méthode 2: Modèle FINE-TUNÉ + Classifieur RandomForest")
    acc3 = evaluate_with_classifier(df)
    print(f"   → Accuracy : {acc3:.3f}\n")

    print("=" * 70)
    print("   RÉSULTATS")
    print("=" * 70)
    print(f"  Méthode 1 (original + seuils)         : {acc1:.3f}")
    print(f"  Méthode 2(fine-tuné + RandomForest)  : {acc3:.3f}")
    print()
    print(f"  Amélioration (Méthode 1 → Méthode 2)  : {(acc3 - acc1) * 100:+.1f} points")
    print("=" * 70)


if __name__ == "__main__":
    main()