# -*- coding: utf-8 -*-
"""Télécharge et prépare les datasets HuggingFace.

À lancer UNE SEULE FOIS.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from datasets import load_dataset
import pandas as pd

RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
RAW.mkdir(parents=True, exist_ok=True)
PROCESSED.mkdir(parents=True, exist_ok=True)

PROFILS_EQUIVALENTS = {
    "Software Engineer": ["Software Engineer", "Backend Developer", "Frontend Developer", "Full Stack Developer"],
    "Data Scientist": ["Data Scientist", "Data Analyst", "Machine Learning Engineer", "ML Engineer", "AI Engineer"],
    "QA Analyst": ["QA Analyst", "QA Engineer", "QA Automation Engineer", "SDET (Software Development Engineer in Test)"],
}


def mapper(role):
    for profil, eq in PROFILS_EQUIVALENTS.items():
        if role in eq:
            return profil
    return None


def download_ankshi():
    cache = RAW / "ankshi_hr.parquet"
    if cache.exists():
        print("✅ Ankshi déjà en cache.")
        return pd.read_parquet(cache)
    print("📥 Téléchargement Ankshi...")
    ds = load_dataset("Ankshi/hr-interview-dataset")
    df = ds["train"].to_pandas().drop_duplicates(subset=["question"])
    df.to_parquet(cache, index=False)
    print(f"✅ Ankshi : {len(df)} questions sauvegardées.")
    return df


def download_davichick():
    cache = RAW / "davichick.parquet"
    if cache.exists():
        print("✅ Davichick déjà en cache.")
        return pd.read_parquet(cache)
    print("📥 Téléchargement Davichick...")
    ds = load_dataset("Davichick/InterviewForge_GenDS", split="train")
    df = ds.to_pandas().drop_duplicates(subset=["question"])
    df.to_parquet(cache, index=False)
    print(f"✅ Davichick : {len(df)} questions sauvegardées.")
    return df


def main():
    df_ankshi = download_ankshi()
    df_dav = download_davichick()

    print("\n🔧 Filtrage par profil...")
    tous_roles = []
    for eq in PROFILS_EQUIVALENTS.values():
        tous_roles.extend(eq)

    df_ankshi_f = df_ankshi[df_ankshi["role"].isin(tous_roles)].copy()
    df_dav_f = df_dav[df_dav["role"].isin(tous_roles)].copy()

    df_ankshi_f["profil"] = df_ankshi_f["role"].apply(mapper)
    df_dav_f["profil"] = df_dav_f["role"].apply(mapper)

    df_all = pd.concat([df_ankshi_f, df_dav_f], ignore_index=True)
    df_all = df_all.drop_duplicates(subset=["question"]).reset_index(drop=True)

    colonnes_utiles = ["question", "profil"]
    for col in ["role", "ideal_answer", "answer", "expected_answer"]:
        if col in df_all.columns:
            colonnes_utiles.append(col)

    df_all = df_all[colonnes_utiles]
    output = PROCESSED / "questions_all.parquet"
    df_all.to_parquet(output, index=False)

    print(f"\n✅ Total : {len(df_all)} questions dans {output}")
    print("\n📊 Répartition :")
    print(df_all["profil"].value_counts())
    print("\n📋 Colonnes :", list(df_all.columns))


if __name__ == "__main__":
    main()