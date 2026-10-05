# -*- coding: utf-8 -*-
"""Entretien 100 % vocal : l'interviewer parle, tu réponds à la voix."""

import sys
import time
from pathlib import Path

# Pour importer `interview` et `voice` depuis le dossier racine
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from interview.engine import RHInterviewEngine
from voice.tts import speak
from voice.stt import listen_and_transcribe


# Durée d'enregistrement par question (secondes)
RECORD_SECONDS = 10


def main():
    print("=" * 60)
    print("   ENTRETIEN RH — VERSION VOCALE")
    print("=" * 60)
    print("L'interviewer va te parler. Tu réponds à voix haute.")
    print(f"Tu as {RECORD_SECONDS} secondes par réponse.")
    print()

    engine = RHInterviewEngine(profile="Software Engineer", n_standard=5)

    question_num = 0
    while True:
        question = engine.get_next_question()
        if question is None:
            break

        question_num += 1
        print(f"\n--- Question {question_num} ---")

        # 1) L'interviewer parle
        print("🎧 L'interviewer parle...")
        speak(question["question"], lang="en", dest_path=f"voice/q{question_num}.mp3")

        # 2) Tu réponds à la voix
        try:
            answer = listen_and_transcribe(duration=RECORD_SECONDS, language="en")
        except Exception as e:
            print(f"⚠️ Erreur d'enregistrement : {e}")
            print("On passe à la question suivante.")
            answer = ""

        print(f"📝 Transcription : {answer!r}")

        # 3) Notation
        evaluation = engine.submit_answer(question, answer)
        print(f"📊 Score    : {evaluation['score']} ({evaluation['quality']})")
        print(f"🔍 Concepts : {evaluation['concepts_found']}")

    # Rapport final
    report = engine.get_report()
    print("\n" + "=" * 60)
    print("   RAPPORT FINAL")
    print("=" * 60)
    print(f"   Score global   : {report['score'] * 100:.1f}%")
    print(f"   Questions      : {report['num_questions']}")
    print(f"   Décision       : {report['decision']}")
    print("=" * 60)

    # 4) L'interviewer annonce la décision
    if report["decision"] == "PASSER AU CTO":
        msg = f"Your final score is {report['score']*100:.0f} percent. You are moving on to the next stage."
    else:
        msg = f"Your final score is {report['score']*100:.0f} percent. We will not continue with your application."
    speak(msg, lang="en", dest_path="voice/final.mp3")


if __name__ == "__main__":
    main()