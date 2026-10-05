# -*- coding: utf-8 -*-
"""Moteur d'entretien RH : pose les questions, note les réponses."""

import random
import time

from interview.questions import STANDARD_RH_QUESTIONS
from interview.evaluator import evaluate_answer


class RHInterviewEngine:
    """Pose des questions RH (5 standard + N aléatoires) et note les réponses."""

    def __init__(self, profile, df=None, n_standard=5, n_random=0):
        self.profile = profile
        self.df = df  # dataframe pandas (facultatif pour l'instant)
        self.n_standard = n_standard
        self.n_random = n_random
        self.history = []
        self.asked_std = set()
        self.asked_rand = set()
        self.start_time = time.time()

    def get_next_question(self):
        """Retourne la prochaine question, ou None si l'entretien est fini."""
        # 1) Questions standard
        if len(self.asked_std) < self.n_standard:
            std = [q for q in STANDARD_RH_QUESTIONS if q["id"] not in self.asked_std]
            if std:
                q = std[0]
                self.asked_std.add(q["id"])
                return {**q, "type": "standard"}

        # 2) Questions aléatoires (si un dataframe est fourni)
        if self.df is not None and len(self.asked_rand) < self.n_random:
            candidates = self.df[~self.df.index.isin(self.asked_rand)]
            if len(candidates) > 0:
                idx = random.choice(candidates.index)
                self.asked_rand.add(idx)
                q = self.df.loc[idx].to_dict()
                return {**q, "type": "random"}

        return None

    def submit_answer(self, question, answer):
        """Évalue une réponse et l'ajoute à l'historique."""
        q_formatted = {
            "ideal_answer": question.get("ideal_answer") or question.get("expected_answer", ""),
            "keywords": question.get("keywords", []),
            "elements": question.get("elements", {}),
        }
        ev = evaluate_answer(q_formatted, answer)
        self.history.append({
            "question": question["question"],
            "answer": answer,
            "evaluation": ev,
            "type": question.get("type", "standard"),
        })
        return ev

    def get_report(self):
        """Rapport final : score global + décision."""
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