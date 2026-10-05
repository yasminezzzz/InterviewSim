# -*- coding: utf-8 -*-
"""Démo texte du simulateur d'entretien RH.

Lance avec :
    python scripts\\run_interview.py
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from interview.engine import RHInterviewEngine


def main():
    print("=" * 60)
    print("   ENTRETIEN RH — SIMULATEUR (version texte)")
    print("=" * 60)
    print("Tape ta réponse puis Entrée. Tape 'quit' pour arrêter.\n")

    engine = RHInterviewEngine(profile="Software Engineer", n_standard=5)

    while True:
        question = engine.get_next_question()
        if question is None:
            break

        print(f"\n[{question['id']}] {question['question']}")
        try:
            answer = input("➡️  Ta réponse : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n(interrompu)")
            break

        if answer.lower() in ("quit", "exit", "q"):
            print("(arrêt demandé)")
            break

        if not answer:
            print("(réponse vide, on passe)")
            answer = ""

        evaluation = engine.submit_answer(question, answer)
        print(f"   📊 Score    : {evaluation['score']} ({evaluation['quality']})")
        print(f"   🔍 Concepts : {evaluation['concepts_found']}")

    # Rapport final
    report = engine.get_report()
    print("\n" + "=" * 60)
    print("   RAPPORT FINAL")
    print("=" * 60)
    print(f"   Score global   : {report['score'] * 100:.1f}%")
    print(f"   Questions      : {report['num_questions']}")
    print(f"   Décision       : {report['decision']}")
    print("=" * 60)


if __name__ == "__main__":
    main()