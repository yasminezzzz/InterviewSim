# -*- coding: utf-8 -*-
"""Évalue le modèle fine-tuné sur le test set : accuracy, F1, matrice de confusion."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

LABEL_TO_SCORE = {
    "Mauvaise": 0.0,
    "Insuffisante": 0.25,
    "Moyenne": 0.5,
    "Bonne": 0.75,
    "Excellente": 1.0,
}

SCORE_TO_LABEL = [
    (0.85, "Excellente"),
    (0.60, "Bonne"),
    (0.40, "Moyenne"),
    (0.20, "Insuffisante"),
    (0.0, "Mauvaise"),
]

BASE = 0.20
MODEL_PATH = ROOT / "models" / "interview-encoder-v7"
TEST_FILE = ROOT / "data" / "test.csv"


def score_to_label(score):
    for threshold, label in SCORE_TO_LABEL:
        if score >= threshold:
            return label
    return "Mauvaise"


def predict(model, ideal, candidate):
    emb1 = model.encode(ideal, convert_to_tensor=True)
    emb2 = model.encode(candidate, convert_to_tensor=True)
    sim = float(util.cos_sim(emb1, emb2)[0][0])
    score = max(0.0, (sim - BASE) / (1.0 - BASE))
    return score_to_label(score)


def main():
    print("=" * 60)
    print("   ÉVALUATION DU MODÈLE SUR LE TEST SET")
    print("=" * 60)

    df = pd.read_csv(TEST_FILE)
    print(f"\n📂 Test set : {len(df)} lignes\n")

    print(f"🧠 Chargement du modèle : {MODEL_PATH.name}")
    model = SentenceTransformer(str(MODEL_PATH))

    y_true = []
    y_pred = []

    for _, row in df.iterrows():
        true_label = row["label"]
        pred_label = predict(model, row["ideal_answer"], row["candidate_answer"])
        y_true.append(true_label)
        y_pred.append(pred_label)

    # Métriques
    acc = accuracy_score(y_true, y_pred)
    print("\n" + "=" * 60)
    print(f"   ACCURACY : {acc:.3f}")
    print("=" * 60)

    print("\n📊 RAPPORT DE CLASSIFICATION :\n")
    labels_order = ["Mauvaise", "Insuffisante", "Moyenne", "Bonne", "Excellente"]
    print(classification_report(y_true, y_pred, labels=labels_order, digits=3))

    print("📊 MATRICE DE CONFUSION :\n")
    cm = confusion_matrix(y_true, y_pred, labels=labels_order)
    print(f"{'':14s}" + "".join(f"{l:12s}" for l in labels_order))
    for i, label in enumerate(labels_order):
        row_str = f"{label:14s}" + "".join(f"{cm[i][j]:<12d}" for j in range(len(labels_order)))
        print(row_str)

    print("\n(Lignes = vrai label, Colonnes = prédiction du modèle)")


if __name__ == "__main__":
    main()