# -*- coding: utf-8 -*-
"""Sépare hr_dataset_v3.csv en train (80%) et test (20%) — stratifié par label."""

import csv
from collections import defaultdict
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "hr_dataset_v3.csv"
TRAIN_OUT = ROOT / "data" / "train.csv"
TEST_OUT = ROOT / "data" / "test.csv"

# Pour la reproductibilité
random.seed(42)


def main():
    # 1. Lire le dataset
    rows = []
    with open(INPUT, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    print(f"📂 {len(rows)} lignes chargées depuis {INPUT}")

    # 2. Grouper par label (pour split stratifié)
    by_label = defaultdict(list)
    for row in rows:
        by_label[row["label"]].append(row)

    # 3. Split 80/20 par label
    train, test = [], []
    for label, items in by_label.items():
        random.shuffle(items)
        n_train = int(len(items) * 0.8)
        train.extend(items[:n_train])
        test.extend(items[n_train:])
        print(f"   {label:12s} : {n_train} train / {len(items) - n_train} test")

    # 4. Mélanger train et test
    random.shuffle(train)
    random.shuffle(test)

    # 5. Écrire les fichiers
    for path, data in [(TRAIN_OUT, train), (TEST_OUT, test)]:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    print(f"\n✅ {len(train)} lignes dans {TRAIN_OUT}")
    print(f"✅ {len(test)} lignes dans {TEST_OUT}")


if __name__ == "__main__":
    main()