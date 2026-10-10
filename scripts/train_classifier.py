# -*- coding: utf-8 -*-
"""Entraîne un RandomForest sur les features extraites."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from scripts.features import extract_features, features_to_vector, FEATURE_NAMES

TRAIN_FILE = ROOT / "data" / "train.csv"
TEST_FILE = ROOT / "data" / "test.csv"
MODEL_OUT = ROOT / "models" / "classifier_rf.pkl"

LABELS_ORDER = ["Mauvaise", "Insuffisante", "Moyenne", "Bonne", "Excellente"]


def build_dataset(df):
    X = []
    y = []
    for _, row in df.iterrows():
        features = extract_features(
            ideal_answer=row["ideal_answer"],
            candidate_answer=row["candidate_answer"],
            keywords=[],
        )
        X.append(features_to_vector(features))
        y.append(row["label"])
    return X, y


def main():
    print("=" * 60)
    print("   ENTRAÎNEMENT DU CLASSIFIEUR RANDOM FOREST")
    print("=" * 60)

    train = pd.read_csv(TRAIN_FILE)
    test = pd.read_csv(TEST_FILE)
    print(f"\n📂 Train : {len(train)} lignes")
    print(f"📂 Test  : {len(test)} lignes")

    print("\n🔧 Extraction des features...")
    X_train, y_train = build_dataset(train)
    X_test, y_test = build_dataset(test)
    print(f"✅ {len(FEATURE_NAMES)} features : {FEATURE_NAMES}")

    print("\n🌲 Entraînement du RandomForest...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42,
    )
    model.fit(X_train, y_train)
    print("✅ Modèle entraîné.")

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print("\n" + "=" * 60)
    print(f"   ACCURACY (test) : {acc:.3f}")
    print("=" * 60)

    print("\n📊 RAPPORT DE CLASSIFICATION :\n")
    print(classification_report(y_test, y_pred, labels=LABELS_ORDER, digits=3, zero_division=0))

    print("📊 MATRICE DE CONFUSION :\n")
    cm = confusion_matrix(y_test, y_pred, labels=LABELS_ORDER)
    print(f"{'':14s}" + "".join(f"{l:14s}" for l in LABELS_ORDER))
    for i, label in enumerate(LABELS_ORDER):
        row_str = f"{label:14s}" + "".join(f"{cm[i][j]:<14d}" for j in range(len(LABELS_ORDER)))
        print(row_str)

    print("\n📊 IMPORTANCE DES FEATURES :\n")
    importances = sorted(zip(FEATURE_NAMES, model.feature_importances_), key=lambda x: -x[1])
    for name, imp in importances:
        print(f"  {name:20s} : {imp:.3f}")

    MODEL_OUT.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_OUT)
    print(f"\n✅ Modèle sauvegardé : {MODEL_OUT}")


if __name__ == "__main__":
    main()