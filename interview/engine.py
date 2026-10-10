# -*- coding: utf-8 -*-
"""Moteur d'entretien RH : 5 standard + N aléatoires."""

import random
import time

from interview.questions import STANDARD_RH_QUESTIONS
from interview.evaluator import evaluate_answer


class RHInterviewEngine:
    def __init__(self, profile, df=None, n_standard=5, n_random=0):
        self.profile = profile
        self.df = None
        self.n_standard = n_standard
        self.n_random = n_random
        self.history = []
        self.asked_std = set()
        self.asked_rand = set()
        self.start_time = time.time()
        self._current_question = None

        if df is None and n_random > 0:
            try:
                from interview.datasets import load_questions_for_profile
                df = load_questions_for_profile(profile)
            except Exception as e:
                print(f"⚠️ Dataset indisponible : {e}")

        if df is not None:
            self.df = df

    def get_next_question(self):
        if self._current_question is not None:
            return self._current_question

        if len(self.asked_std) < self.n_standard:
            std = [q for q in STANDARD_RH_QUESTIONS if q["id"] not in self.asked_std]
            if std:
                q = std[0]
                self.asked_std.add(q["id"])
                self._current_question = {**q, "type": "standard"}
                return self._current_question

        if self.df is not None and len(self.asked_rand) < self.n_random:
            candidates = self.df[~self.df.index.isin(self.asked_rand)]
            if len(candidates) > 0:
                idx = random.choice(candidates.index)
                self.asked_rand.add(idx)
                q = self.df.loc[idx].to_dict()
                self._current_question = {**q, "type": "random"}
                return self._current_question

        return None

    def submit_answer(self, question, answer):
        q_formatted = {
            "ideal_answer": question.get("ideal_answer") or question.get("expected_answer", ""),
            "keywords": question.get("keywords", []),
            "elements": question.get("elements", {}),
        }
        ev = evaluate_answer(q_formatted, answer)
        self.history.append({
            "question": question["question"],
            "question_full": question,
            "answer": answer,
            "evaluation": ev,
            "type": question.get("type", "standard"),
        })
        self._current_question = None
        return ev

    def get_report(self):
        if not self.history:
            return {"score": 0, "decision": "REJETÉ", "num_questions": 0}

        std = [h["evaluation"]["score"] for h in self.history if h["type"] == "standard"]
        rand = [h["evaluation"]["score"] for h in self.history if h["type"] == "random"]
        avg = sum(h["evaluation"]["score"] for h in self.history) / len(self.history)

        return {
            "profile": self.profile,
            "score": round(avg, 3),
            "standard_score": round(sum(std) / len(std), 3) if std else 0,
            "random_score": round(sum(rand) / len(rand), 3) if rand else 0,
            "num_standard": len(std),
            "num_random": len(rand),
            "num_questions": len(self.history),
            "decision": "PASSER AU CTO" if avg >= 0.5 else "REJETÉ",
        }


if __name__ == "__main__":
    print("✅ engine OK")
    engine = RHInterviewEngine(profile="Software Engineer", n_standard=5, n_random=0)
    q = engine.get_next_question()
    print(f"Q1 : {q['question']}")
    ev = engine.submit_answer(q, "I'm a software engineer with 3 years of experience.")
    print(f"Score : {ev['score']} ({ev['quality']})")